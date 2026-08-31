import { useState } from 'react'
import { ArrowRight, Shield, Zap, BookOpen, Users } from 'lucide-react'

export default function Landing() {
  const [email, setEmail] = useState('')
  const [subscribed, setSubscribed] = useState(false)

  const handleSubscribe = (e) => {
    e.preventDefault()
    if (email) {
      setSubscribed(true)
      setEmail('')
      setTimeout(() => setSubscribed(false), 3000)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">⚖</div>
            <span className="text-lg font-semibold text-gray-900">Juriscope</span>
          </div>
          <a
            href="/app"
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            Launch App
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            AI-Powered Legal Document Analysis
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Upload legal documents and get instant answers using semantic search and generative AI. Juriscope makes legal research faster and more accessible.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/app"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start Free <ArrowRight size={18} />
            </a>
            <a
              href="#features"
              className="inline-flex items-center justify-center px-6 py-3 bg-gray-100 text-gray-900 font-medium rounded-lg hover:bg-gray-200 transition-colors"
            >
              Learn More
            </a>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Powerful Features</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Everything you need for professional legal document analysis
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Feature 1 */}
            <div className="bg-white p-8 rounded-lg border border-gray-200">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <BookOpen className="text-blue-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Semantic Search</h3>
              <p className="text-gray-600">
                Find relevant passages instantly using advanced AI embeddings. No more keyword-only searches—ask questions in natural language.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white p-8 rounded-lg border border-gray-200">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Zap className="text-blue-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Instant Answers</h3>
              <p className="text-gray-600">
                Get precise, grounded answers directly from your documents. Juriscope uses RAG (Retrieval-Augmented Generation) for accuracy.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white p-8 rounded-lg border border-gray-200">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Shield className="text-blue-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Document Tracing</h3>
              <p className="text-gray-600">
                Every answer includes citations to the source documents. Verify results and build confidence in the analysis.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-white p-8 rounded-lg border border-gray-200">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Users className="text-blue-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Session Management</h3>
              <p className="text-gray-600">
                Maintain conversation history across queries. Ask follow-up questions and build context over time.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold text-gray-900 mb-16 text-center">How It Works</h2>

          <div className="space-y-12">
            {/* Step 1 */}
            <div className="flex gap-6">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-semibold text-sm">
                  1
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload Your Documents</h3>
                <p className="text-gray-600">
                  Add PDF or text files containing legal documents. Juriscope automatically processes and indexes them.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex gap-6">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-semibold text-sm">
                  2
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Ask Questions</h3>
                <p className="text-gray-600">
                  Type any question about your documents in natural language. The AI understands legal terminology and context.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex gap-6">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-semibold text-sm">
                  3
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Get Answers with Sources</h3>
                <p className="text-gray-600">
                  Receive precise answers grounded in your documents. Every answer shows which documents it came from.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">Built with Advanced Technology</h2>
          <p className="text-lg text-gray-600 mb-12">
            Juriscope combines cutting-edge AI models and vector search to deliver unprecedented accuracy.
          </p>

          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <p className="text-sm font-medium text-gray-600 mb-2">LLM</p>
              <p className="text-lg font-semibold text-gray-900">Qwen 27B</p>
              <p className="text-xs text-gray-500 mt-1">via Groq API</p>
            </div>
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <p className="text-sm font-medium text-gray-600 mb-2">Vector DB</p>
              <p className="text-lg font-semibold text-gray-900">Pinecone</p>
              <p className="text-xs text-gray-500 mt-1">Semantic search</p>
            </div>
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <p className="text-sm font-medium text-gray-600 mb-2">Embeddings</p>
              <p className="text-lg font-semibold text-gray-900">MPNet</p>
              <p className="text-xs text-gray-500 mt-1">768-dimensional</p>
            </div>
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <p className="text-sm font-medium text-gray-600 mb-2">Backend</p>
              <p className="text-lg font-semibold text-gray-900">FastAPI</p>
              <p className="text-xs text-gray-500 mt-1">Python 3.13</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Ready to Get Started?</h2>
          <p className="text-lg text-gray-600 mb-8">
            Launch the app and upload your first legal document today.
          </p>
          <a
            href="/app"
            className="inline-flex items-center justify-center gap-2 px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors text-lg"
          >
            Launch App <ArrowRight size={20} />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-12 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">⚖</div>
              <span className="font-semibold text-gray-900">Juriscope</span>
            </div>
            <p className="text-sm text-gray-600">
              AI-powered legal document analysis. Built for accuracy and speed.
            </p>
            <p className="text-sm text-gray-500">
              © 2026 Juriscope. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
