import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../services/api'

export default function Chat() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    api.post('/chat/sessions').then((res) => setSession(res.data))
  }, [user, navigate])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [session?.messages])

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || !session) return
    setLoading(true)
    const message = input
    setInput('')
    try {
      const res = await api.post(`/chat/sessions/${session.id}/message`, { content: message })
      setSession((s) => ({
        ...s,
        messages: [...s.messages, ...res.data],
      }))
    } catch {
      setInput(message)
    } finally {
      setLoading(false)
    }
  }

  const suggestions = [
    'Show me properties in Mumbai under ₹1 crore',
    'Compare properties in Bangalore and Pune',
    'Which property has the most parking?',
    'Recommend a 3BHK in Delhi',
  ]

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">AI Real Estate Assistant</h1>
      <p className="text-slate-500 mb-6">Ask questions about listed properties. Answers are grounded in our database.</p>

      <div className="bg-white rounded-xl border border-slate-200 flex flex-col" style={{ height: '500px' }}>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {session?.messages?.length === 0 && (
            <div className="text-center py-8">
              <p className="text-slate-400 mb-4">Try asking:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {suggestions.map((s) => (
                  <button key={s} onClick={() => setInput(s)}
                    className="text-sm bg-slate-100 hover:bg-slate-200 px-3 py-2 rounded-lg text-slate-600">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {session?.messages?.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-xl px-4 py-3 text-sm ${
                msg.role === 'user' ? 'bg-primary-600 text-white' : 'bg-slate-100 text-slate-800'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}
          {loading && <p className="text-sm text-slate-400">Thinking...</p>}
          <div ref={bottomRef} />
        </div>

        <form onSubmit={sendMessage} className="border-t border-slate-200 p-4 flex gap-3">
          <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about properties..."
            className="flex-1 border border-slate-300 rounded-lg px-4 py-2 text-sm" />
          <button type="submit" disabled={loading}
            className="bg-primary-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50">
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
