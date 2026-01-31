import { useState } from 'react';
import { useSettings, useUpdateSettings, useHealth } from '../hooks/useApi';
import { Save, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

export default function Settings() {
  const { data: settings, isLoading } = useSettings();
  const { data: health } = useHealth();
  const updateSettings = useUpdateSettings();
  
  const [formData, setFormData] = useState(settings || {});
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await updateSettings.mutateAsync(formData);
  };
  
  if (isLoading) {
    return <div className="flex items-center justify-center h-full">
      <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
    </div>;
  }
  
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Settings</h1>
      
      {/* System Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">System Status</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatusCard label="API" status={health?.status} />
          <StatusCard label="Database" status={health?.database} />
          <StatusCard label="RabbitMQ" status={health?.rabbitmq} />
          <StatusCard label="Qdrant" status={health?.qdrant} />
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Azure OpenAI */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Azure OpenAI</h2>
          <div className="space-y-4">
            <InputField label="Endpoint" value={formData.azure_openai_endpoint} onChange={(v) => setFormData({...formData, azure_openai_endpoint: v})} />
            <InputField label="API Key" type="password" value={formData.azure_openai_key} onChange={(v) => setFormData({...formData, azure_openai_key: v})} />
            <InputField label="GPT-4 Deployment" value={formData.azure_openai_deployment_gpt4} onChange={(v) => setFormData({...formData, azure_openai_deployment_gpt4: v})} />
            <InputField label="Embedding Deployment" value={formData.azure_openai_deployment_embed} onChange={(v) => setFormData({...formData, azure_openai_deployment_embed: v})} />
          </div>
        </div>
        
        {/* Azure Document Intelligence */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Azure Document Intelligence</h2>
          <div className="space-y-4">
            <InputField label="Endpoint" value={formData.azure_doc_intelligence_endpoint} onChange={(v) => setFormData({...formData, azure_doc_intelligence_endpoint: v})} />
            <InputField label="API Key" type="password" value={formData.azure_doc_intelligence_key} onChange={(v) => setFormData({...formData, azure_doc_intelligence_key: v})} />
          </div>
        </div>
        
        {/* RAG Parameters */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">RAG Parameters</h2>
          <div className="grid grid-cols-2 gap-4">
            <InputField label="Chunk Size" type="number" value={formData.chunk_size} onChange={(v) => setFormData({...formData, chunk_size: parseInt(v)})} />
            <InputField label="Chunk Overlap" type="number" value={formData.chunk_overlap} onChange={(v) => setFormData({...formData, chunk_overlap: parseInt(v)})} />
            <InputField label="Retrieval Top K" type="number" value={formData.retrieval_top_k} onChange={(v) => setFormData({...formData, retrieval_top_k: parseInt(v)})} />
            <InputField label="Reranking Top K" type="number" value={formData.reranking_top_k} onChange={(v) => setFormData({...formData, reranking_top_k: parseInt(v)})} />
            <InputField label="RRF K" type="number" value={formData.rrf_k} onChange={(v) => setFormData({...formData, rrf_k: parseInt(v)})} />
            <InputField label="Agent Max Iterations" type="number" value={formData.agent_max_iterations} onChange={(v) => setFormData({...formData, agent_max_iterations: parseInt(v)})} />
          </div>
        </div>
        
        <button
          type="submit"
          disabled={updateSettings.isPending}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {updateSettings.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
          Save Settings
        </button>
      </form>
    </div>
  );
}

function StatusCard({ label, status }: { label: string; status?: string }) {
  const isHealthy = status === 'healthy' || status === 'connected';
  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-center gap-2">
        {isHealthy ? <CheckCircle className="w-5 h-5 text-green-500" /> : <AlertCircle className="w-5 h-5 text-red-500" />}
        <span className="font-medium">{label}</span>
      </div>
      <div className="text-sm text-gray-500 mt-1">{status || 'Unknown'}</div>
    </div>
  );
}

function InputField({ label, value, onChange, type = 'text' }: any) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type={type}
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );
}
