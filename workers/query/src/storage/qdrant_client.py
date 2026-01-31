import logging
from typing import List, Dict, Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import ScoredPoint
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

class QdrantHybridSearch:
    """Hybrid search using vector + BM25 with RRF fusion"""
    
    def __init__(self, host: str, port: int, collection: str, rrf_k: int = 60):
        self.client = AsyncQdrantClient(host=host, port=port)
        self.collection = collection
        self.rrf_k = rrf_k
    
    async def hybrid_search(
        self,
        query_embedding: List[float],
        query_text: str,
        top_k: int = 20,
        document_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform hybrid search with vector + BM25 + RRF fusion
        
        Returns:
            {
                "chunks": List[Dict],
                "search_sources": {
                    "vector_chunks": int,
                    "vector_summaries": int,
                    "vector_qa": int,
                    "keyword_bm25": int,
                    "after_merge": int
                }
            }
        """
        logger.info(f"Performing hybrid search with query: {query_text[:100]}...")
        
        search_sources = {
            "vector_chunks": 0,
            "vector_summaries": 0,
            "vector_qa": 0,
            "keyword_bm25": 0,
            "after_merge": 0
        }
        
        # 1. Vector search for text chunks
        vector_chunks = await self._vector_search(
            query_embedding,
            filter_type="text_chunk",
            top_k=top_k,
            document_ids=document_ids
        )
        search_sources["vector_chunks"] = len(vector_chunks)
        
        # 2. Vector search for summaries
        vector_summaries = await self._vector_search(
            query_embedding,
            filter_type="summary",
            top_k=5,
            document_ids=document_ids
        )
        search_sources["vector_summaries"] = len(vector_summaries)
        
        # 3. Vector search for Q&A
        vector_qa = await self._vector_search(
            query_embedding,
            filter_type="qa",
            top_k=5,
            document_ids=document_ids
        )
        search_sources["vector_qa"] = len(vector_qa)
        
        # 4. BM25 keyword search
        bm25_chunks = await self._bm25_search(query_text, top_k=top_k, document_ids=document_ids)
        search_sources["keyword_bm25"] = len(bm25_chunks)
        
        # 5. RRF fusion
        merged_chunks = self._rrf_fusion([vector_chunks, vector_summaries, vector_qa, bm25_chunks])
        search_sources["after_merge"] = len(merged_chunks)
        
        logger.info(f"Hybrid search: {search_sources['vector_chunks']} vector chunks, "
                   f"{search_sources['vector_summaries']} summaries, "
                   f"{search_sources['vector_qa']} Q&A, "
                   f"{search_sources['keyword_bm25']} BM25 → {search_sources['after_merge']} merged")
        
        return {
            "chunks": merged_chunks[:top_k],
            "search_sources": search_sources
        }
    
    async def _vector_search(
        self,
        query_embedding: List[float],
        filter_type: str,
        top_k: int,
        document_ids: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Perform vector search with type filter"""
        try:
            # Build filter
            filter_conditions = {"must": [{"key": "type", "match": {"value": filter_type}}]}
            
            if document_ids:
                filter_conditions["must"].append({
                    "key": "document_id",
                    "match": {"any": document_ids}
                })
            
            # Search
            results = await self.client.search(
                collection_name=self.collection,
                query_vector=query_embedding,
                query_filter=filter_conditions,
                limit=top_k
            )
            
            # Convert to dict format
            chunks = []
            for result in results:
                chunks.append({
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "type": result.payload.get("type", ""),
                    "section": result.payload.get("section", ""),
                    "document_id": result.payload.get("document_id", ""),
                    "metadata": result.payload.get("metadata", {})
                })
            
            return chunks
        
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def _bm25_search(
        self,
        query_text: str,
        top_k: int,
        document_ids: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Perform BM25 keyword search"""
        try:
            # Scroll through all text chunks (or specific documents)
            filter_conditions = {"must": [{"key": "type", "match": {"value": "text_chunk"}}]}
            
            if document_ids:
                filter_conditions["must"].append({
                    "key": "document_id",
                    "match": {"any": document_ids}
                })
            
            # Get all chunks (simplified - in production, you'd want pagination)
            results, _ = await self.client.scroll(
                collection_name=self.collection,
                scroll_filter=filter_conditions,
                limit=1000  # Limit for performance
            )
            
            if not results:
                return []
            
            # Prepare BM25
            corpus = [point.payload.get("text", "") for point in results]
            tokenized_corpus = [doc.lower().split() for doc in corpus]
            bm25 = BM25Okapi(tokenized_corpus)
            
            # Score query
            tokenized_query = query_text.lower().split()
            scores = bm25.get_scores(tokenized_query)
            
            # Get top K
            ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            
            chunks = []
            for idx in ranked_indices:
                point = results[idx]
                chunks.append({
                    "id": point.id,
                    "score": float(scores[idx]),
                    "text": point.payload.get("text", ""),
                    "type": point.payload.get("type", ""),
                    "section": point.payload.get("section", ""),
                    "document_id": point.payload.get("document_id", ""),
                    "metadata": point.payload.get("metadata", {})
                })
            
            return chunks
        
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []
    
    def _rrf_fusion(self, ranked_lists: List[List[Dict]]) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion to merge multiple ranked lists
        
        RRF score = sum(1 / (k + rank)) for each list
        """
        # Collect all unique chunks by ID
        chunk_scores = {}
        chunk_data = {}
        
        for ranked_list in ranked_lists:
            for rank, chunk in enumerate(ranked_list, start=1):
                chunk_id = chunk["id"]
                
                # Store chunk data
                if chunk_id not in chunk_data:
                    chunk_data[chunk_id] = chunk
                
                # Accumulate RRF score
                rrf_score = 1.0 / (self.rrf_k + rank)
                chunk_scores[chunk_id] = chunk_scores.get(chunk_id, 0.0) + rrf_score
        
        # Sort by RRF score
        sorted_chunks = sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return chunks with updated scores
        merged = []
        for chunk_id, score in sorted_chunks:
            chunk = chunk_data[chunk_id].copy()
            chunk["rrf_score"] = score
            merged.append(chunk)
        
        return merged
