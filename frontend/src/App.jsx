import { useState, useRef, useEffect, useCallback } from 'react'
import axios from "axios"
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

const INITIAL_MESSAGE = {
  id: 0,
  role: "bot",
  text: "Bonjour et bienvenue chez Vala Creative Internet Solutions\u00a0! Comment puis-je vous aider\u00a0?",
  sources: [],
  timestamp: new Date(),
  isError: false,
}

function formatTime(date) {
  return date.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })
}

function BotAvatar() {
  return (
    <div className="bot-avatar" aria-hidden="true">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
      </svg>
    </div>
  )
}

export default function App() {
  const [isOpen, setIsOpen] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [messages, setMessages] = useState([INITIAL_MESSAGE])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)
  const nextId = useRef(1)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isOpen])

  // Auto-grow the textarea as the user types
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = "auto"
    ta.style.height = Math.min(ta.scrollHeight, 120) + "px"
  }, [input])

  const sendMessage = useCallback(async (questionOverride) => {
    const question = questionOverride ?? input
    if (!question.trim() || loading) return

    const userMsg = {
      id: nextId.current++,
      role: "user",
      text: question,
      sources: [],
      timestamp: new Date(),
      isError: false,
    }

    setMessages(prev => [...prev, userMsg])
    setInput("")
    setLoading(true)

    try {
      const response = await axios.post(`${API_URL}/chat`, { question })
      setMessages(prev => [...prev, {
        id: nextId.current++,
        role: "bot",
        text: response.data.answer,
        sources: response.data.sources,
        timestamp: new Date(),
        isError: false,
      }])
    } catch {
      setMessages(prev => [...prev, {
        id: nextId.current++,
        role: "bot",
        text: "Désolé, une erreur s'est produite. Veuillez réessayer.",
        sources: [],
        timestamp: new Date(),
        isError: true,
        retryQuestion: question,
      }])
    } finally {
      setLoading(false)
    }
  }, [input, loading])

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setMessages([{ ...INITIAL_MESSAGE, timestamp: new Date() }])
    nextId.current = 1
  }

  return (
    <div className="widget-container">

      {/* ── Chat Window ── */}
      {isOpen && (
        <div className={`chat-box ${isExpanded ? "expanded" : ""}`} role="dialog" aria-label="Vala Support Chat">

          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-left">
              <div className="header-avatar" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                </svg>
              </div>
              <div>
                <div className="chat-title">Vala Support</div>
                <div className="chat-subtitle">
                  <span className="status-dot" aria-hidden="true" />
                  Répond en quelques secondes
                </div>
              </div>
            </div>
            <div className="chat-header-actions">
              <button
                id="clear-chat-btn"
                className="icon-btn"
                onClick={clearChat}
                title="Effacer la conversation"
                aria-label="Effacer la conversation"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6l-1 14H6L5 6"/>
                  <path d="M10 11v6M14 11v6"/>
                  <path d="M9 6V4h6v2"/>
                </svg>
              </button>
              <button
                id="expand-chat-btn"
                className="icon-btn"
                onClick={() => setIsExpanded(prev => !prev)}
                title={isExpanded ? "Réduire" : "Agrandir"}
                aria-label={isExpanded ? "Réduire la fenêtre" : "Agrandir la fenêtre"}
              >
                {isExpanded ? (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/>
                    <line x1="10" y1="14" x2="3" y2="21"/><line x1="21" y1="3" x2="14" y2="10"/>
                  </svg>
                ) : (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/>
                    <line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/>
                  </svg>
                )}
              </button>
              <button
                id="close-chat-btn"
                className="icon-btn"
                onClick={() => setIsOpen(false)}
                title="Fermer"
                aria-label="Fermer le chat"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                  <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="chat-messages" role="log" aria-live="polite">
            {messages.map((msg) => (
              <div key={msg.id} className={`message-group ${msg.role}`}>

                {msg.role === "bot" && <BotAvatar />}

                <div className="message-content">
                  <div className={`bubble ${msg.role} ${msg.isError ? "error" : ""}`}>
                    {msg.text}
                  </div>

                  {msg.isError && msg.retryQuestion && (
                    <button
                      className="retry-btn"
                      onClick={() => sendMessage(msg.retryQuestion)}
                      disabled={loading}
                      aria-label="Réessayer"
                    >
                      ↺ Réessayer
                    </button>
                  )}

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources" role="complementary" aria-label="Sources">
                      <div className="sources-label">Sources</div>
                      {msg.sources.map((src, j) => (
                        <a
                          key={j}
                          href={src.url}
                          target="_blank"
                          rel="noreferrer"
                          className="source-link"
                        >
                          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                            <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
                          </svg>
                          {src.title}
                        </a>
                      ))}
                    </div>
                  )}

                  <div className="message-time" aria-label={`Envoyé à ${formatTime(msg.timestamp)}`}>
                    {formatTime(msg.timestamp)}
                  </div>
                </div>

              </div>
            ))}

            {loading && (
              <div className="message-group bot" aria-label="Le bot est en train d'écrire">
                <BotAvatar />
                <div className="bubble bot typing" aria-hidden="true">
                  <span /><span /><span />
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="chat-input-area">
            <textarea
              ref={textareaRef}
              id="chat-input"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Écrivez votre message…"
              rows={1}
              disabled={loading}
              aria-label="Message à envoyer"
              aria-multiline="true"
            />
            <button
              id="send-btn"
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className="send-btn"
              aria-label="Envoyer le message"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* ── Floating Button ── */}
      <button
        id="fab-btn"
        className={`fab ${isOpen ? "fab-open" : ""}`}
        onClick={() => setIsOpen(prev => !prev)}
        aria-label={isOpen ? "Fermer le chat" : "Ouvrir le chat"}
        aria-expanded={isOpen}
      >
        {isOpen ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        ) : (
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
          </svg>
        )}
      </button>

    </div>
  )
}