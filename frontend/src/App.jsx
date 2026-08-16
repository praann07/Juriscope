import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import './index.css'

function UploadModal({ onClose, onSuccess }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState('')
  const [dragOver, setDragOver] = useState(false)

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setStatus('Uploading and indexing document...')
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await fetch('/upload', { method: 'POST', body: form })
      const data = await res.json()
      if (res.ok) {
        setStatus(`✅ ${data.message} — ${data.chunks} chunks indexed${data.pages ? `, ${data.pages} pages` : ''}`)
        setTimeout(() => { onSuccess(file.name); onClose() }, 2000)
      } else {
        setStatus(`❌ ${data.detail}`)
        setUploading(false)
      }
    } catch {
      setStatus('❌ Upload failed. Is the backend running on port 8000?')
      setUploading(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) setFile(dropped)
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-2xl border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-gray-900">Upload Legal Document</h2>
            <p className="text-xs text-gray-500 mt-0.5">PDF or TXT · Max 20MB</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>

        <label
          className={`block w-full border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-400 hover:bg-blue-50'}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
        >
          <input type="file" accept=".pdf,.txt" className="hidden" onChange={e => setFile(e.target.files[0])} />
          {file ? (
            <div>
              <p className="text-3xl mb-2">📄</p>
              <p className="text-sm font-semibold text-gray-800">{file.name}</p>
              <p className="text-xs text-gray-400 mt-1">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          ) : (
            <div>
              <p className="text-3xl mb-2">📂</p>
              <p className="text-sm font-medium text-gray-600">Drop file here or click to browse</p>
              <p className="text-xs text-gray-400 mt-1">Supports PDF and TXT</p>
            </div>
          )}
        </label>

        {status && (
          <div className={`mt-3 p-3 rounded-lg text-sm text-center ${status.startsWith('✅') ? 'bg-green-50 text-green-700' : status.startsWith('❌') ? 'bg-red-50 text-red-700' : 'bg-blue-50 text-blue-700'}`}>
            {status}
          </div>
        )}

        <div className="flex gap-3 mt-5">
          <button onClick={onClose} disabled={uploading} className="flex-1 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50">
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white rounded-xl text-sm font-semibold transition-colors"
          >
            {uploading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                Indexing...
              </span>
            ) : 'Upload & Index'}
          </button>
        </div>
      </div>
    </div>
  )
}

const SAMPLE_QUESTIONS = [
  "Who are the parties and what maintenance was awarded?",
  "From what date should maintenance be paid?",
  "What guidelines did the Supreme Court lay down?",
  "What were the lower court orders before this appeal?",
]

function MessageContent({ content }) {
  return (
    <ReactMarkdown
      components={{
        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
        ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
        li: ({ children }) => <li className="text-sm">{children}</li>,
        strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
        h1: ({ children }) => <h1 className="font-bold text-base mb-1">{children}</h1>,
        h2: ({ children }) => <h2 className="font-bold text-sm mb-1">{children}</h2>,
        h3: ({ children }) => <h3 className="font-semibold text-sm mb-1">{children}</h3>,
        code: ({ children }) => <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono">{children}</code>,
        blockquote: ({ children }) => <blockquote className="border-l-2 border-blue-300 pl-3 italic text-gray-600 my-2">{children}</blockquote>,
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [backendOnline, setBackendOnline] = useState(false)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [indexedDocs, setIndexedDocs] = useState(['lawsuit.txt'])
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    const check = async () => {
      try {
        const r = await fetch('/api/health')
        setBackendOnline(r.ok)
      } catch {
        setBackendOnline(false)
      }
    }
    check()
    const interval = setInterval(check, 5000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async (text) => {
    const query = (text || input).trim()
    if (!query || loading) return
    setInput('')
    inputRef.current?.focus()

    setMessages(prev => [...prev, {
      role: 'user',
      content: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }])
    setLoading(true)

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: query, session_id: sessionId })
      })
      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Server error')
      }

      if (!sessionId && data.session_id) setSessionId(data.session_id)

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `**Error:** ${err.message || 'Could not reach the backend. Make sure FastAPI is running on port 8000.'}`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        error: true
      }])
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
    <div className="flex flex-col h-screen bg-gray-50 font-sans">

      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-3.5 flex items-center justify-between shadow-sm shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center shadow-sm">
            <span className="text-white text-base">⚖️</span>
          </div>
          <div>
            <h1 className="text-base font-bold text-gray-900 leading-tight">Juriscope</h1>
            <p className="text-[11px] text-gray-400">AI-Powered Legal Document Assistant</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border ${backendOnline ? 'bg-green-50 text-green-700 border-green-200' : 'bg-red-50 text-red-600 border-red-200'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${backendOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></span>
            {backendOnline ? 'Online' : 'Offline'}
          </div>

          {messages.length > 0 && (
            <button onClick={handleReset} className="text-xs text-gray-500 hover:text-red-500 border border-gray-200 hover:border-red-200 px-3 py-1.5 rounded-lg transition-colors">
              Clear Chat
            </button>
          )}

          <button
            onClick={() => setUploadOpen(true)}
            className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition-colors font-semibold flex items-center gap-1.5"
          >
            <span>+</span> Upload Doc
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">

        {/* Sidebar */}
        <aside className="w-60 bg-white border-r border-gray-100 flex flex-col p-4 gap-5 shrink-0 overflow-y-auto">
          <div>
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Indexed Documents</p>
            <div className="space-y-1.5">
              {indexedDocs.map((doc, i) => (
                <div key={i} className="flex items-center gap-2 p-2.5 bg-blue-50 border border-blue-100 rounded-lg">
                  <span className="text-blue-500 text-sm shrink-0">📄</span>
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-gray-800 truncate">{doc}</p>
                    <span className="text-[10px] text-green-600 font-semibold">● Indexed</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Stack</p>
            <div className="space-y-1.5 text-xs text-gray-500">
              {[['🧠', 'Llama 3.3 · Groq'], ['📦', 'Pinecone Vector DB'], ['⚡', 'FastAPI'], ['🔗', 'LangChain']].map(([icon, label]) => (
                <div key={label} className="flex items-center gap-2 px-2 py-1.5 bg-gray-50 rounded-lg">
                  <span>{icon}</span><span>{label}</span>
                </div>
              ))}
            </div>
          </div>

          {sessionId && (
            <div className="mt-auto">
              <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">Session ID</p>
              <p className="text-[10px] text-gray-400 font-mono bg-gray-50 p-2 rounded-lg break-all">{sessionId.substring(0, 20)}...</p>
            </div>
          )}
        </aside>

        {/* Chat */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">

            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center gap-8">
                <div>
                  <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <span className="text-3xl">⚖️</span>
                  </div>
                  <h2 className="text-xl font-bold text-gray-800">Ask a Legal Question</h2>
                  <p className="text-gray-400 text-sm mt-2 max-w-sm">
                    Query your indexed legal documents using natural language. Powered by Llama 3.3 via Groq.
                  </p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-2xl">
                  {SAMPLE_QUESTIONS.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(q)}
                      className="text-left p-3.5 bg-white border border-gray-200 rounded-xl text-sm text-gray-600 hover:border-blue-400 hover:bg-blue-50 hover:text-blue-700 transition-all shadow-sm"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center shrink-0 mt-1 shadow-sm">
                    <span className="text-white text-xs">⚖</span>
                  </div>
                )}

                <div className={`max-w-2xl flex flex-col gap-1 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-sm'
                      : msg.error
                        ? 'bg-red-50 text-red-700 border border-red-200 rounded-tl-sm'
                        : 'bg-white text-gray-800 border border-gray-200 shadow-sm rounded-tl-sm'
                  }`}>
                    {msg.role === 'assistant'
                      ? <MessageContent content={msg.content} />
                      : msg.content
                    }
                  </div>
                  <span className="text-[10px] text-gray-400 px-1">{msg.time}</span>
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center shrink-0 mt-1">
                    <span className="text-gray-500 text-xs">👤</span>
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center shrink-0 shadow-sm">
                  <span className="text-white text-xs">⚖</span>
                </div>
                <div className="bg-white border border-gray-200 shadow-sm rounded-2xl rounded-tl-sm px-4 py-3.5">
                  <div className="flex gap-1 items-center">
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-200 bg-white px-6 py-4 shrink-0">
            <div className="flex gap-3 max-w-4xl mx-auto">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                placeholder="Ask a question about the indexed legal documents..."
                className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50 focus:bg-white transition-colors"
                disabled={loading}
                maxLength={2000}
              />
              <button
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-200 disabled:text-gray-400 text-white px-5 py-3 rounded-xl text-sm font-semibold transition-colors"
              >
                Send
              </button>
            </div>
            <p className="text-center text-[11px] text-gray-400 mt-2">
              Answers are grounded strictly in indexed legal documents · Powered by Llama 3.3 via Groq
            </p>
          </div>
        </main>
      </div>

      {uploadOpen && (
        <UploadModal
          onClose={() => setUploadOpen(false)}
          onSuccess={(name) => setIndexedDocs(prev => prev.includes(name) ? prev : [...prev, name])}
        />
      )}
    </div>
  )
}
