import asyncio
import json
import logging
import time
from typing import Dict, Any

from aio_pika import connect_robust, IncomingMessage
from config import settings
from pipeline.embedder import QueryEmbedder
from pipeline.reranker import Reranker
from pipeline.agent import Agent
from pipeline.generator import Generator
from storage.qdrant_client import QdrantHybridSearch
from storage.postgres_client import PostgresStorage

logger = logging.getLogger(__name__)

class QueryConsumer:
    """Consume query jobs from RabbitMQ and execute agentic RAG"""
    
    def __init__(self):
        self.settings = settings
        
        # Initialize pipeline components
        self.embedder = QueryEmbedder(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            deployment=settings.azure_openai_deployment_embed,
            api_version=settings.azure_openai_api_version
        )
        
        self.qdrant = QdrantHybridSearch(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            collection=settings.qdrant_collection,
            rrf_k=settings.rrf_k
        )
        
        self.reranker = Reranker(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            deployment=settings.azure_openai_deployment_gpt4,
            api_version=settings.azure_openai_api_version
        )
        
        self.agent = Agent(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            deployment=settings.azure_openai_deployment_gpt4,
            api_version=settings.azure_openai_api_version
        )
        
        self.generator = Generator(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            deployment=settings.azure_openai_deployment_gpt4,
            api_version=settings.azure_openai_api_version
        )
        
        self.postgres = PostgresStorage(connection_string=settings.postgres_url)
    
    async def process_query(self, job_data: Dict[str, Any]):
        """
        Process a query through the agentic RAG pipeline
        
        Agentic Loop:
        1. Embed query
        2. Hybrid search (vector + BM25 + RRF)
        3. Rerank top chunks
        4. Agent evaluates sufficiency
        5. If insufficient, refine query and repeat (max 3 iterations)
        6. Generate final answer with citations
        """
        query_id = job_data.get("query_id")
        query_text = job_data.get("query_text")
        document_ids = job_data.get("document_ids")
        
        logger.info(f"Processing query {query_id}: {query_text}")
        
        # Track debug data
        iterations_data = []
        timing = {}
        
        try:
            # Update status to processing
            await self.postgres.update_query_result(query_id, "processing")
            
            # Agentic loop
            current_query = query_text
            final_chunks = []
            
            for iteration in range(1, self.settings.agent_max_iterations + 1):
                logger.info(f"Iteration {iteration}/{self.settings.agent_max_iterations}")
                iteration_start = time.time()
                
                iteration_timing = {}
                
                # 1. Embed query
                embed_start = time.time()
                query_embedding = await self.embedder.embed_query(current_query)
                iteration_timing["embedding_ms"] = int((time.time() - embed_start) * 1000)
                
                # 2. Hybrid search
                search_start = time.time()
                search_result = await self.qdrant.hybrid_search(
                    query_embedding=query_embedding,
                    query_text=current_query,
                    top_k=self.settings.retrieval_top_k,
                    document_ids=document_ids
                )
                iteration_timing["search_ms"] = int((time.time() - search_start) * 1000)
                
                chunks = search_result.get("chunks", [])
                search_sources = search_result.get("search_sources", {})
                
                # Store chunks before rerank
                chunks_before_rerank = chunks[:self.settings.reranking_top_k]
                
                # 3. Rerank
                rerank_start = time.time()
                reranked_chunks = await self.reranker.rerank(
                    current_query,
                    chunks,
                    top_k=self.settings.reranking_top_k
                )
                iteration_timing["rerank_ms"] = int((time.time() - rerank_start) * 1000)
                
                # 4. Agent evaluation
                agent_start = time.time()
                agent_eval = await self.agent.evaluate(
                    query=current_query,
                    chunks=reranked_chunks,
                    iteration=iteration,
                    max_iterations=self.settings.agent_max_iterations
                )
                iteration_timing["agent_ms"] = int((time.time() - agent_start) * 1000)
                
                # Calculate total iteration duration
                iteration_timing["total_ms"] = int((time.time() - iteration_start) * 1000)
                
                # Store iteration data
                iterations_data.append({
                    "iteration_number": iteration,
                    "query_used": current_query,
                    "search_sources": search_sources,
                    "chunks_before_rerank": [
                        {
                            "id": c.get("id"),
                            "score": c.get("score", c.get("rrf_score", 0)),
                            "text": c.get("text", "")[:200],
                            "section": c.get("section", "")
                        }
                        for c in chunks_before_rerank
                    ],
                    "chunks_after_rerank": [
                        {
                            "id": c.get("id"),
                            "score": c.get("score", c.get("rrf_score", 0)),
                            "text": c.get("text", "")[:200],
                            "section": c.get("section", ""),
                            "rerank_position": c.get("rerank_position")
                        }
                        for c in reranked_chunks
                    ],
                    "agent_evaluation": agent_eval,
                    "timing": iteration_timing
                })
                
                # Check agent decision
                decision = agent_eval.get("decision", "proceed")
                
                if decision == "proceed":
                    final_chunks = reranked_chunks
                    break
                elif decision == "refine_query":
                    refined_query = agent_eval.get("refined_query")
                    if refined_query:
                        current_query = refined_query
                        logger.info(f"Refining query to: {refined_query}")
                    else:
                        # No refined query provided, proceed with current chunks
                        final_chunks = reranked_chunks
                        break
                elif decision == "expand_search":
                    # For expand, we'll increase top_k in next iteration
                    # For now, just continue with current chunks
                    final_chunks = reranked_chunks
                else:
                    # Unknown decision, proceed
                    final_chunks = reranked_chunks
                    break
            
            # 5. Generate final answer
            gen_start = time.time()
            result = await self.generator.generate_answer(query_text, final_chunks)
            gen_time = int((time.time() - gen_start) * 1000)
            
            # Build timing summary
            timing = {
                "embedding_ms": sum(it["timing"]["embedding_ms"] for it in iterations_data),
                "search_ms": sum(it["timing"]["search_ms"] for it in iterations_data),
                "rerank_ms": sum(it["timing"]["rerank_ms"] for it in iterations_data),
                "agent_ms": sum(it["timing"]["agent_ms"] for it in iterations_data),
                "generation_ms": gen_time,
                "total_ms": sum(it["timing"]["total_ms"] for it in iterations_data) + gen_time
            }
            
            # Build debug data
            debug_data = {
                "iterations": iterations_data,
                "timing": timing
            }
            
            # Update query with results
            await self.postgres.update_query_result(
                query_id=query_id,
                status="completed",
                answer=result.get("answer"),
                citations=result.get("citations"),
                debug_data=debug_data
            )
            
            logger.info(f"Successfully processed query {query_id} in {timing['total_ms']}ms with {len(iterations_data)} iterations")
        
        except Exception as e:
            logger.error(f"Failed to process query {query_id}: {e}", exc_info=True)
            
            # Update query status to failed
            await self.postgres.update_query_result(
                query_id=query_id,
                status="failed",
                error_message=str(e)
            )
    
    async def on_message(self, message: IncomingMessage):
        """Handle incoming RabbitMQ message"""
        async with message.process():
            try:
                # Parse job data
                job_data = json.loads(message.body.decode())
                logger.info(f"Received job: {job_data}")
                
                # Process query
                await self.process_query(job_data)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    
    async def start(self):
        """Start consuming from RabbitMQ"""
        logger.info("Starting query worker")
        
        # Connect to PostgreSQL
        await self.postgres.connect()
        
        # Connect to RabbitMQ
        connection = await connect_robust(self.settings.rabbitmq_url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        
        # Declare queue
        queue = await channel.declare_queue("query_processing", durable=True)
        
        # Start consuming
        logger.info("Waiting for messages from query_processing queue")
        await queue.consume(self.on_message)
        
        # Keep running
        try:
            await asyncio.Future()
        finally:
            await connection.close()
            await self.postgres.close()
