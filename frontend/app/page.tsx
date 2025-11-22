'use client';

import { useState } from 'react';

export default function Home() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/v1/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setResponse(data.response);
    } catch (error) {
      setResponse('Error: Failed to get response from the API');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            ☀️ Solar PV LLM AI
          </h1>
          <p className="text-gray-600">
            AI-powered Solar PV knowledge system for beginners to experts
          </p>
        </div>

        {/* Query Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask anything about Solar PV systems..."
              className="w-full p-4 pr-24 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={4}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="absolute bottom-4 right-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Thinking...' : 'Ask'}
            </button>
          </div>
        </form>

        {/* Response */}
        {response && (
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">Response</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{response}</p>
          </div>
        )}

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-2">🎓 For All Levels</h3>
            <p className="text-gray-600 text-sm">
              From beginners learning the basics to experts seeking technical details
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-2">📚 RAG-Powered</h3>
            <p className="text-gray-600 text-sm">
              Retrieval-augmented generation with citations from trusted sources
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-2">🔄 Continuous Learning</h3>
            <p className="text-gray-600 text-sm">
              Incrementally trained on the latest solar PV research and data
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
