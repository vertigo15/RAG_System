import { Card } from '../components/common/Card';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { StatusIndicator } from '../components/common/StatusIndicator';
import { useSettings } from '../hooks/useSettings';
import { Spinner } from '../components/common/Spinner';
import { useState, useEffect } from 'react';

export default function Settings() {
  const { settings, health, isLoading, updateSettings, isUpdating } = useSettings();
  const [formData, setFormData] = useState(settings || {});

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
            {health.services.map((service: any) => (
              <StatusIndicator key={service.name} status={service} />
            ))}
          </div>
        </Card>
      )}

      {/* Azure OpenAI Configuration */}
      <Card title="Azure OpenAI Configuration">
        <form onSubmit={handleSubmit} className="space-y-4">
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
            />
            <Input
              label="LLM Model"
              value={formData.azure_openai_deployment_gpt4 || ''}
              onChange={(e) => setFormData({ ...formData, azure_openai_deployment_gpt4: e.target.value })}
            />
          </div>
          <Button type="submit" loading={isUpdating}>
            💾 Save Settings
          </Button>
        </form>
      </Card>

      {/* RAG Configuration */}
      <Card title="RAG Configuration">
        <div className="grid grid-cols-3 gap-4">
          <Input
            label="Top K Results"
            type="number"
            value={formData.retrieval_top_k || 10}
            onChange={(e) => setFormData({ ...formData, retrieval_top_k: parseInt(e.target.value) })}
          />
          <Input
            label="Rerank Top"
            type="number"
            value={formData.reranking_top_k || 5}
            onChange={(e) => setFormData({ ...formData, reranking_top_k: parseInt(e.target.value) })}
          />
          <Input
            label="Max Iterations"
            type="number"
            value={formData.agent_max_iterations || 3}
            onChange={(e) => setFormData({ ...formData, agent_max_iterations: parseInt(e.target.value) })}
          />
        </div>
      </Card>
    </div>
  );
}
