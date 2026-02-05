import { Card } from '../components/common/Card';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { useSettings } from '../hooks/useSettings';
import { Spinner } from '../components/common/Spinner';
import { useState, useEffect } from 'react';
import type { Settings } from '../types';

export default function Settings() {
  const { settings, health, isLoading, updateSettings, isUpdating } = useSettings();
  const [formData, setFormData] = useState<Partial<Settings>>({});

  useEffect(() => {
    if (settings) {
      setFormData(settings);
    }
  }, [settings]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateSettings(formData);
  };

  return (
    <div className="max-w-7xl mx-auto px-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">⚙️ Settings</h1>

      {/* System Status */}
      {health?.services && (
        <Card title="System Status">
          <div className="space-y-2">
            {Object.entries(health.services).map(([name, service]: [string, any]) => {
              const displayName = name === 'postgres' ? 'PostgreSQL' 
                : name === 'rabbitmq' ? 'RabbitMQ'
                : name === 'qdrant' ? 'Qdrant'
                : name === 'azure_openai' ? 'Azure OpenAI'
                : name;
              
              const statusIcon = service.status === 'connected' ? '🟢' 
                : service.status === 'disconnected' ? '🔴'
                : service.status === 'degraded' ? '🟡'
                : '⚪';
              
              return (
                <div key={name} className="flex items-center justify-between py-2 px-3 rounded-lg bg-gray-50">
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{statusIcon}</span>
                    <div>
                      <div className="font-medium text-gray-900">{displayName}</div>
                    </div>
                  </div>
                  <div className="text-sm text-gray-600">
                    {service.message || service.status}
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Azure OpenAI Configuration */}
      <Card title="Azure OpenAI Configuration">
        <div className="space-y-4">
          <Input
            label="Endpoint"
            value={formData.azure_openai_endpoint || ''}
            onChange={(e) => setFormData({ ...formData, azure_openai_endpoint: e.target.value })}
            placeholder="https://your-resource.openai.azure.com/"
          />
          <Input
            label="API Key"
            type="password"
            value={formData.azure_openai_key || ''}
            onChange={(e) => setFormData({ ...formData, azure_openai_key: e.target.value })}
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Embedding Model"
              value={formData.azure_openai_deployment_embed || ''}
              onChange={(e) => setFormData({ ...formData, azure_openai_deployment_embed: e.target.value })}
              placeholder="text-embedding-3-large"
            />
            <Input
              label="LLM Model"
              value={formData.azure_openai_deployment_gpt4 || ''}
              onChange={(e) => setFormData({ ...formData, azure_openai_deployment_gpt4: e.target.value })}
              placeholder="gpt-4"
            />
          </div>
        </div>
      </Card>

      {/* Azure Document Intelligence Configuration */}
      <Card title="Azure Document Intelligence">
        <div className="space-y-4">
          <Input
            label="Endpoint"
            value={formData.azure_doc_intelligence_endpoint || ''}
            onChange={(e) => setFormData({ ...formData, azure_doc_intelligence_endpoint: e.target.value })}
            placeholder="https://your-resource.cognitiveservices.azure.com/"
          />
          <Input
            label="API Key"
            type="password"
            value={formData.azure_doc_intelligence_key || ''}
            onChange={(e) => setFormData({ ...formData, azure_doc_intelligence_key: e.target.value })}
          />
        </div>
      </Card>

      {/* RAG Configuration */}
      <Card title="RAG Configuration">
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <Input
              label="Top K Results"
              type="number"
              value={formData.retrieval_top_k || 10}
              onChange={(e) => setFormData({ ...formData, retrieval_top_k: parseInt(e.target.value) })}
              min={1}
              max={50}
            />
            <Input
              label="Rerank Top"
              type="number"
              value={formData.reranking_top_k || 5}
              onChange={(e) => setFormData({ ...formData, reranking_top_k: parseInt(e.target.value) })}
              min={1}
              max={20}
            />
            <Input
              label="Max Iterations"
              type="number"
              value={formData.agent_max_iterations || 3}
              onChange={(e) => setFormData({ ...formData, agent_max_iterations: parseInt(e.target.value) })}
              min={1}
              max={10}
            />
          </div>
          <div className="flex items-center gap-6">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.enable_hybrid_search ?? true}
                onChange={(e) => setFormData({ ...formData, enable_hybrid_search: e.target.checked })}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">Enable Hybrid Search</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.enable_qa_matching ?? true}
                onChange={(e) => setFormData({ ...formData, enable_qa_matching: e.target.checked })}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">Enable Q&A Matching</span>
            </label>
          </div>
        </div>
      </Card>

      {/* Chunking Configuration */}
      <Card title="Chunking Configuration">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Settings */}
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Basic Settings</h4>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Chunk Size (tokens)"
                type="number"
                value={formData.chunk_size || 500}
                onChange={(e) => setFormData({ ...formData, chunk_size: parseInt(e.target.value) })}
                min={100}
                max={2000}
              />
              <Input
                label="Chunk Overlap (tokens)"
                type="number"
                value={formData.chunk_overlap || 50}
                onChange={(e) => setFormData({ ...formData, chunk_overlap: parseInt(e.target.value) })}
                min={0}
                max={500}
              />
            </div>
          </div>

          {/* Semantic Chunker Settings */}
          <div className="border-t pt-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Semantic Chunker</h4>
            <div className="space-y-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.semantic_overlap_enabled ?? true}
                  onChange={(e) => setFormData({ ...formData, semantic_overlap_enabled: e.target.checked })}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Enable overlap between sections</span>
              </label>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Overlap Tokens"
                  type="number"
                  value={formData.semantic_overlap_tokens || 50}
                  onChange={(e) => setFormData({ ...formData, semantic_overlap_tokens: parseInt(e.target.value) })}
                  min={10}
                  max={200}
                  disabled={!formData.semantic_overlap_enabled}
                />
              </div>
            </div>
          </div>

          {/* Hierarchical Chunker Settings */}
          <div className="border-t pt-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Hierarchical Chunker</h4>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Parent Size Multiplier"
                  type="number"
                  step="0.1"
                  value={formData.parent_chunk_multiplier || 2.0}
                  onChange={(e) => setFormData({ ...formData, parent_chunk_multiplier: parseFloat(e.target.value) })}
                  min={1.5}
                  max={4.0}
                />
                <Input
                  label="Parent Summary Max Length"
                  type="number"
                  value={formData.parent_summary_max_length || 300}
                  onChange={(e) => setFormData({ ...formData, parent_summary_max_length: parseInt(e.target.value) })}
                  min={100}
                  max={500}
                />
              </div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.use_llm_for_parent_summary ?? false}
                  onChange={(e) => setFormData({ ...formData, use_llm_for_parent_summary: e.target.checked })}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Use LLM for parent summaries (increases cost)</span>
              </label>
            </div>
          </div>

          {/* Auto-Selection Thresholds */}
          <div className="border-t pt-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Auto-Selection Thresholds</h4>
            <div className="grid grid-cols-3 gap-4">
              <Input
                label="Hierarchical (chars)"
                type="number"
                value={formData.hierarchical_threshold_chars || 60000}
                onChange={(e) => setFormData({ ...formData, hierarchical_threshold_chars: parseInt(e.target.value) })}
                min={20000}
                max={200000}
              />
              <Input
                label="Semantic (chars)"
                type="number"
                value={formData.semantic_threshold_chars || 12000}
                onChange={(e) => setFormData({ ...formData, semantic_threshold_chars: parseInt(e.target.value) })}
                min={5000}
                max={50000}
              />
              <Input
                label="Min Headers for Semantic"
                type="number"
                value={formData.min_headers_for_semantic || 3}
                onChange={(e) => setFormData({ ...formData, min_headers_for_semantic: parseInt(e.target.value) })}
                min={1}
                max={10}
              />
            </div>
          </div>

          <Button type="submit" loading={isUpdating}>
            💾 Save Settings
          </Button>
        </form>
      </Card>
    </div>
  );
}
