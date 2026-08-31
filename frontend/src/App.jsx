import { useState, useEffect, useRef } from 'react'
import { Send, Plus, Trash2, Menu, X, Loader, AlertCircle, CheckCircle, FileText, ArrowRight } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import './index.css'

// Landing Page Component
function Landing({ onStart }) {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">⚖</div>
            <span className="text-lg font-semibold text-gray-900">Juriscope</span>
          </div>
          <button
            onClick={onStart}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            Launch App
          </button>
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
            <button
              onClick={onStart}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start Free <ArrowRight size={18} />
            </button>
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
            <div className="bg-white p-8 rounded-lg border border-gray-200">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <FileText className="text-blue-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Semantic Search</h3>
              <p className="text-gray-600">
                Find relevant passages instantly using advanced AI embeddings. No more keyword-only searches.
              </p>
            </div>

            <div className="bg-white p-8 rounded-lg border border-gray-200">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Loader className="text-blue-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Instant Answers</h3>
              <p className="text-gray-600">
                Get precise, grounded answers directly from your documents using RAG technology.
              </p>
            </div>

            <div className="bg-white p-8 rounded-lg border border-gray-200">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <CheckCircle className="text-blue-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Document Tracing</h3>
              <p className="text-gray-600">
                Every answer includes citations to source documents. Verify results instantly.
              </p>
            </div>

            <div className="bg-white p-8 rounded-lg border border-gray-200">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Menu className="text-blue-600" size={24} />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Session Management</h3>
              <p className="text-gray-600">
                Maintain conversation history across queries. Ask follow-up questions with context.
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
            <div className="flex gap-6">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-semibold">1</div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload Your Documents</h3>
                <p className="text-gray-600">Add PDF or text files. Juriscope automatically processes and indexes them.</p>
              </div>
            </div>

            <div className="flex gap-6">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-semibold">2</div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Ask Questions</h3>
                <p className="text-gray-600">Type any question in natural language. The AI understands legal terminology.</p>
              </div>
            </div>

            <div className="flex gap-6">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-semibold">3</div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Get Answers with Sources</h3>
                <p className="text-gray-600">Receive precise answers with citations to the source documents.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-24 px-6 bg-gray-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">Built with Advanced Technology</h2>

          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <p className="text-sm font-medium text-gray-600 mb-2">LLM</p>
              <p className="text-lg font-semibold text-gray-900">Qwen 27B</p>
              <p className="text-xs text-gray-500 mt-1">via Groq</p>
            </div>
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <p className="text-sm font-medium text-gray-600 mb-2">Vector DB</p>
              <p className="text-lg font-semibold text-gray-900">Pinecone</p>
              <p className="text-xs text-gray-500 mt-1">Semantic Search</p>
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
          <p className="text-lg text-gray-600 mb-8">Launch the app and upload your first legal document today.</p>
          <button
            onClick={onStart}
            className="inline-flex items-center justify-center gap-2 px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors text-lg"
          >
            Launch App <ArrowRight size={20} />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-12 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">⚖</div>
            <span className="font-semibold text-gray-900">Juriscope</span>
          </div>
          <p className="text-sm text-gray-600">AI-powered legal document analysis. Built for accuracy and speed.</p>
          <p className="text-sm text-gray-500">© 2026 Juriscope. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

// Upload Modal Component
function DocumentUploadModal({ isOpen, onClose, onSuccess }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError('')
    setStatus('Uploading and indexing...')

    const form = new FormData()
    form.append('file', file)

    try {
      const res = await fetch('/upload', { method: 'POST', body: form })
      const data = await res.json()

      if (res.ok) {
        setStatus(`✓ Indexed ${data.chunks} chunks`)
        setTimeout(() => {
          onSuccess(file.name)
          onClose()
          setFile(null)
          setStatus('')
        }, 1500)
      } else {
        setError(data.detail || 'Upload failed')
        setUploading(false)
      }
    } catch (err) {
      setError('Backend is not running. Make sure FastAPI is on port 8000.')
      setUploading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Upload Legal Document</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close modal"
          >
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 hover:bg-blue-50 transition-colors cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
          >
            <FileText size={32} className="mx-auto text-gray-400 mb-2" />
            <p className="font-medium text-gray-900">{file?.name || 'Choose file or drag here'}</p>
            <p className="text-sm text-gray-600 mt-1">PDF or TXT · Max 20MB</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              disabled={uploading}
            />
          </div>

          {error && (
            <div className="flex gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle size={18} className="text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {status && (
            <div className="flex gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              {uploading ? (
                <Loader size={18} className="text-blue-600 flex-shrink-0 animate-spin mt-0.5" />
              ) : (
                <CheckCircle size={18} className="text-green-600 flex-shrink-0 mt-0.5" />
              )}
              <p className="text-sm text-blue-700">{status}</p>
            </div>
          )}
        </div>

        <div className="flex gap-3 p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            disabled={uploading}
            className="flex-1 px-4 py-2 text-gray-700 font-medium rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="flex-1 px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      </div>
    </div>
  )
}

// Chat Message Component
function ChatMessage({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-xs sm:max-w-md lg:max-w-lg px-4 py-3 rounded-lg ${
          isUser
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-gray-100 text-gray-900 rounded-bl-none'
        }`}
      >
        {message.error ? (
          <div className="flex gap-2">
            <AlertCircle size={18} className="flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-sm">Error</p>
              <p className="text-sm mt-1 opacity-90">{message.content}</p>
            </div>
          </div>
        ) : (
          <div className={`text-sm leading-relaxed`}>
            {isUser ? (
              message.content
            ) : (
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                  ul: ({ children }) => (
                    <ul className="list-disc pl-4 mb-2 space-y-1">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal pl-4 mb-2 space-y-1">
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => <li>{children}</li>,
                  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                  em: ({ children }) => <em className="italic">{children}</em>,
                  h1: ({ children }) => <h1 className="font-bold text-base mb-1">{children}</h1>,
                  h2: ({ children }) => <h2 className="font-bold text-sm mb-1">{children}</h2>,
                  code: ({ children }) => (
                    <code className="bg-gray-200 px-1 py-0.5 rounded text-xs font-mono">
                      {children}
                    </code>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
          </div>
        )}

        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-current border-opacity-20">
            <p className="text-xs font-medium mb-1 opacity-80">Sources:</p>
            <div className="space-y-0.5">
              {message.sources.map((source, idx) => (
                <p key={idx} className="text-xs opacity-80">
                  • {source.source}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Main App Component
export default function App() {
  const [currentPage, setCurrentPage] = useState('landing')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [backendOnline, setBackendOnline] = useState(false)
  const [modelName, setModelName] = useState('')
  const [uploadOpen, setUploadOpen] = useState(false)
  const [indexedDocs, setIndexedDocs] = useState(['lawsuit.txt', 'sorry_letter_aws.pdf'])
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Health check
  useEffect(() => {
    const check = async () => {
      try {
        const r = await fetch('/')
        if (r.ok) {
          const data = await r.json()
          setBackendOnline(true)
          if (data.model) setModelName(data.model)
        }
      } catch {
        setBackendOnline(false)
      }
    }

    check()
    const interval = setInterval(check, 5000)
    return () => clearInterval(interval)
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  if (currentPage === 'landing') {
    return <Landing onStart={() => setCurrentPage('chat')} />
  }

  const sendMessage = async (text) => {
    const query = (text || input).trim()
    if (!query || loading || !backendOnline) return

    setInput('')
    inputRef.current?.focus()

    const userMessage = {
      role: 'user',
      content: query,
    }
    setMessages((prev) => [...prev, userMessage])
    setLoading(true)

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: query, session_id: sessionId }),
      })

      let data = {}
      try {
        data = await res.json()
      } catch {
        data = {}
      }

      if (!res.ok) {
        const errorMsg =
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail || data)
        throw new Error(errorMsg || 'Server error')
      }

      if (!sessionId && data.session_id) {
        setSessionId(data.session_id)
      }

      const assistantMessage = {
        role: 'assistant',
        content: data.response || 'No response from the backend.',
        sources: data.sources || [],
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      const assistantMessage = {
        role: 'assistant',
        content: err.message || 'Could not reach the backend.',
        error: true,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleReset = async () => {
    if (sessionId) {
      await fetch(`/session/reset/${sessionId}`, { method: 'POST' }).catch(() => {})
    }
    setMessages([])
    setSessionId(null)
  }

  return (
    <div className="h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-200 px-4 sm:px-6 py-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? (
              <X size={20} className="text-gray-600" />
            ) : (
              <Menu size={20} className="text-gray-600" />
            )}
          </button>
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            ⚖
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Juriscope</h1>
            <p className="text-xs text-gray-500">Legal Document AI</p>
          </div>
          <button
            onClick={() => setCurrentPage('landing')}
            className="ml-auto lg:ml-0 text-sm text-gray-600 hover:text-gray-900 font-medium"
          >
            ← Back
          </button>
        </div>

        <div className="flex items-center gap-3">
          <div
            className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
              backendOnline
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                backendOnline
                  ? 'bg-green-500 animate-pulse'
                  : 'bg-red-500'
              }`}
            />
            {backendOnline ? 'Connected' : 'Offline'}
          </div>

          {messages.length > 0 && (
            <button
              onClick={handleReset}
              className="hidden sm:flex items-center gap-1.5 px-3 py-2 text-gray-700 text-sm font-medium border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Trash2 size={16} />
              Clear
            </button>
          )}

          <button
            onClick={() => setUploadOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus size={16} />
            <span className="hidden sm:inline">Upload</span>
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside
          className={`${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          } lg:translate-x-0 fixed lg:static inset-y-0 left-0 w-64 bg-gray-50 border-r border-gray-200 p-4 flex flex-col gap-4 overflow-y-auto z-40 transition-transform`}
        >
          <div>
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Indexed Documents
            </p>
            <div className="space-y-2">
              {indexedDocs.map((doc, i) => (
                <div
                  key={i}
                  className="flex items-center gap-2 p-3 bg-white border border-gray-200 rounded-lg"
                >
                  <FileText size={16} className="text-blue-600 flex-shrink-0" />
                  <span className="text-sm text-gray-700 truncate">{doc}</span>
                  <span className="text-xs text-green-600 font-medium ml-auto flex-shrink-0">
                    ✓
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Model Information
            </p>
            <div className="space-y-2 text-sm">
              <div>
                <p className="text-xs text-gray-600">LLM</p>
                <p className="font-medium text-gray-900">{modelName || 'Loading...'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Vector Database</p>
                <p className="font-medium text-gray-900">Pinecone</p>
              </div>
              <div>
                <p className="text-xs text-gray-600">Embeddings</p>
                <p className="font-medium text-gray-900">MPNet 768d</p>
              </div>
            </div>
          </div>

          {messages.length > 0 && (
            <div className="pt-4 border-t border-gray-200">
              <button
                onClick={handleReset}
                className="lg:hidden w-full flex items-center justify-center gap-2 px-3 py-2 text-gray-700 text-sm font-medium border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <Trash2 size={16} />
                Clear Chat
              </button>
            </div>
          )}
        </aside>

        {/* Main Chat */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <FileText size={32} className="text-blue-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Ask a Question
                </h2>
                <p className="text-gray-600 max-w-sm mb-6">
                  Upload legal documents, then ask questions about them. Juriscope will search the documents and provide answers with citations.
                </p>
                <button
                  onClick={() => setUploadOpen(true)}
                  className="px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Upload Your First Document
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                {messages.map((message, idx) => (
                  <ChatMessage key={idx} message={message} />
                ))}
                {loading && (
                  <div className="flex justify-start mb-4">
                    <div className="px-4 py-3 bg-gray-100 rounded-lg rounded-bl-none">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: '0.1s' }}
                        />
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: '0.2s' }}
                        />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4 sm:p-6 bg-white flex-shrink-0">
            {!backendOnline && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex gap-3">
                <AlertCircle size={18} className="text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">
                  Backend is offline. Make sure FastAPI is running on port 8000.
                </p>
              </div>
            )}

            <form
              onSubmit={(e) => {
                e.preventDefault()
                sendMessage()
              }}
              className="flex gap-3"
            >
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={
                  backendOnline
                    ? 'Ask a question about your legal documents...'
                    : 'Waiting for backend...'
                }
                disabled={loading || !backendOnline}
                className="flex-1 px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white disabled:opacity-50 transition-colors text-gray-900"
                autoFocus
              />
              <button
                type="submit"
                disabled={!input.trim() || loading || !backendOnline}
                className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center gap-2"
              >
                {loading ? (
                  <Loader size={18} className="animate-spin" />
                ) : (
                  <Send size={18} />
                )}
                <span className="hidden sm:inline">Send</span>
              </button>
            </form>

            <p className="text-xs text-gray-500 mt-3 text-center">
              Every answer includes citations to the source documents.
            </p>
          </div>
        </main>
      </div>

      {/* Upload Modal */}
      <DocumentUploadModal
        isOpen={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onSuccess={(docName) => {
          if (!indexedDocs.includes(docName)) {
            setIndexedDocs((prev) => [...prev, docName])
          }
        }}
      />
    </div>
  )
}
