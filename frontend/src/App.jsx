import { useState, useRef, useEffect } from 'react'
import axios from "axios";
import './App.css'

const API_URL = "http://localhost:8000"

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "Bonjour! Je suis l'assistant support de Vala. Comment puis-je vous aider?",
      sources: []
    }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: "user", text: input}
    setMessages(prev => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      const response = await axios.post('${API_URL}/chat', {
        question: input
      })
      
      const botMessage = {
        role: "bot",
        text: response.data.answer,
        sources: response.data.sources
      }
      setMessages(prev => [...prev, botMessage])

    } catch(error){
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
    <div className='app'>
      {/* Header */}
      <div className='header'>
        <div>
          <h1>Vala Chatbot</h1>
        </div>
      </div>

      {/* Chat Window */}
      <div className='chat-window'>
        {messages.map((msg,i) => (
          <div key={i} className={'message-row ${msg.role}'}>
            <div className={'bubble ${msg.role}'}>
              <p>{msg.text}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className='sources'>
                  <p className='sources-title'>Sources:</p>
                  {msg.sources.map((src, j) => (
                    <a
                     key={j}
                     href={src.url}
                     target="_blank"
                     rel="noreferrer"
                     className="source-link"
                    >
                      {src.title}
                    </a>          
                  ))}
                </div>
              )}
            </div>
          </div>       
        ))}

      {/* Loading */}
        {loading && (
          <div className='message-row bot'>
            <div className='bubble bot loading'>
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

      {/* AutoScroll */}
        <div ref={bottomRef} />
      </div>
      {/* Input Area */}
      <div className='input-area'>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder='Posez votre question...'
          rows={1}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          {loading ? "..." : "Envoyer"}
        </button>
      </div>

    </div>
  )

}