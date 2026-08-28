import { useState, useRef, useEffect } from 'react'
import axios from "axios";
import './App.css'

const API_URL = "http://localhost:8000"

export default function App() {
  const [isOpen, setIsOpen] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Bonjour et bienvenue chez Vala Creative Internet Solutions, comment puis-je vous aider?",
      sources: []
    }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isOpen])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: "user", text: input}
    setMessages(prev => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        question: input
      })
      setMessages(prev => [...prev, {
        role: "bot",
        text: response.data.answer,
        sources: response.data.sources
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: "bot",
        text: "Désolé, une erreur s'est produite. Veuillez réessayer.",
        sources: []
      }])
    } finally{
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey){
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="widget-container">

      {/* ── Chat Window ── */}
      {isOpen && (
        <div className={`chat-box ${isExpanded ? "expanded" : ""}`}>

          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-left">
              <div>
                <div className="chat-title">Vala Support</div>
                <div className="chat-subtitle">Répond en quelques secondes</div>
              </div>
            </div>
            <div className="chat-header-actions">
              <button
                className="icon-btn"
                onClick={() => setIsExpanded(prev => !prev)}
                title={isExpanded ? "Réduire" : "Agrandir"}
              >
                {isExpanded ? "⊡" : "⊞"}
              </button>
              <button
                className="icon-btn"
                onClick={() => setIsOpen(false)}
                title="Fermer"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`message-group ${msg.role}`}>

                {msg.role === "bot"}

                <div className="message-content">
                  <div className={`bubble ${msg.role}`}>
                    {msg.text}
                  </div>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources">
                      <div className="sources-label">Sources:</div>
                      {msg.sources.map((src, j) => (
                        <a
                          key={j}
                          href={src.url}
                          target="_blank"
                          rel="noreferrer"
                          className="source-link"
                        >
                          ↗ {src.title}
                        </a>
                      ))}
                    </div>
                  )}
                </div>

              </div>
            ))}

            {loading && (
              <div className="message-group bot">
                <div className="bubble bot typing">
                  <span /><span /><span />
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="chat-input-area">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Écrivez votre message..."
              rows={1}
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="send-btn"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </div>

          {/* Footer */}
          <div className="chat-footer">
            Propulsé par <strong>Vala AI</strong>
          </div>

        </div>
      )}

      {/* ── Floating Button ── */}
      <button
        className={`fab ${isOpen ? "fab-open" : ""}`}
        onClick={() => setIsOpen(prev => !prev)}
      >
        {isOpen ? (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/>
          </svg>
        )}
      </button>

    </div>
  )

}