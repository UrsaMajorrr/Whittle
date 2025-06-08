import React, { useState, FormEvent, ChangeEvent } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { PaperAirplaneIcon } from '@heroicons/react/24/solid'

// Backend API base URL
const BACKEND_URL = 'http://localhost:8000'

type AgentType = 'cad' | 'mesh' | 'simulation' | null;

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface AgentInfo {
  name: string
  description: string
  endpoint: string
  color: string
}

type AgentConfig = {
  [K in Exclude<AgentType, null>]: AgentInfo
}

function App(): JSX.Element {
  const [selectedAgent, setSelectedAgent] = useState<AgentType>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const agentConfig: AgentConfig = {
    cad: {
      name: 'CAD Agent',
      description: 'Specialized in computer-aided design and 3D modeling',
      endpoint: '/api/agent/cad/chat',
      color: 'blue'
    },
    mesh: {
      name: 'Meshing Agent',
      description: 'Expert in generating and optimizing simulation meshes',
      endpoint: '/api/agent/mesh/chat',
      color: 'green'
    },
    simulation: {
      name: 'Simulation Agent',
      description: 'Focused on physics simulation and analysis',
      endpoint: '/api/agent/simulation/chat',
      color: 'purple'
    }
  }

  const handleAgentSelect = (agent: AgentType) => {
    setSelectedAgent(agent)
    setMessages([]) // Clear messages when switching agents
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!input.trim() || isLoading || !selectedAgent) return

    const userMessage = input.trim()
    console.log('Sending message:', userMessage)
    
    setInput('')
    setMessages(prev => {
      console.log('Adding user message:', { role: 'user', content: userMessage })
      return [...prev, { role: 'user' as const, content: userMessage }]
    })
    setIsLoading(true)

    try {
      // Use the BACKEND_URL with the endpoint
      const response = await fetch(`${BACKEND_URL}${agentConfig[selectedAgent].endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          history: messages
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log('Received response data:', {
        response: data.response,
        responseType: typeof data.response,
        responseLength: data.response?.length
      })
      
      if (!data.response) {
        console.error('Response missing content:', data)
        throw new Error('Invalid response format')
      }

      const newMessage = { 
        role: 'assistant' as const, 
        content: data.response 
      }
      console.log('Adding assistant message:', newMessage)
      
      setMessages(prev => {
        const updated = [...prev, newMessage]
        console.log('Messages after update:', updated.map(m => ({
          role: m.role,
          contentPreview: m.content?.substring(0, 50),
          contentLength: m.content?.length
        })))
        return updated
      })
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, { 
        role: 'assistant' as const, 
        content: 'Sorry, I encountered an error. Please try again.' 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  // Debug log for messages updates
  React.useEffect(() => {
    console.log('Current messages state:', messages.map(m => ({
      role: m.role,
      contentPreview: m.content?.substring(0, 50),
      contentLength: m.content?.length
    })))
  }, [messages])

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Agent Selection Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-4">
          <h2 className="text-lg font-bold text-gray-900 mb-4">
            Engineering Agents
          </h2>
          <div className="space-y-2">
            {(Object.keys(agentConfig) as Array<Exclude<AgentType, null>>).map((agent) => (
              <button
                key={agent}
                onClick={() => handleAgentSelect(agent)}
                className={`w-full p-3 rounded-lg text-left transition-colors
                  ${selectedAgent === agent 
                    ? `bg-${agentConfig[agent].color}-100 border-${agentConfig[agent].color}-500 border` 
                    : 'hover:bg-gray-50'}`}
              >
                <div className="font-medium text-gray-900">
                  {agentConfig[agent].name}
                </div>
                <div className="text-sm text-gray-500">
                  {agentConfig[agent].description}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col">
        {selectedAgent ? (
          <>
            {/* Agent Header */}
            <header className="bg-white shadow">
              <div className="max-w-7xl mx-auto py-4 px-4">
                <h1 className={`text-2xl font-bold text-${agentConfig[selectedAgent].color}-700`}>
                  {agentConfig[selectedAgent].name}
                </h1>
                <p className="text-gray-500">
                  {agentConfig[selectedAgent].description}
                </p>
              </div>
            </header>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
              {messages.length === 0 ? (
                <div className="text-center text-gray-500">
                  No messages yet. Start a conversation!
                </div>
              ) : (
                messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-3xl rounded-lg px-4 py-2 shadow-md ${
                        message.role === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-white text-gray-900'
                      }`}
                    >
                      <div className="text-xs mb-1 opacity-75">
                        {message.role === 'user' ? 'You' : agentConfig[selectedAgent].name}
                      </div>
                      <div className="whitespace-pre-wrap break-words">
                        <ReactMarkdown 
                          remarkPlugins={[remarkGfm]}
                          className="prose prose-sm max-w-none"
                        >
                          {message.content || '(Empty message)'}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                ))
              )}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white rounded-lg px-4 py-2 text-gray-500 shadow-md">
                    <div className="animate-pulse">Thinking...</div>
                  </div>
                </div>
              )}
            </div>

            {/* Debug Info */}
            {import.meta.env.DEV && (
              <div className="fixed bottom-0 right-0 bg-black bg-opacity-75 text-white p-4 m-4 rounded-lg max-w-lg max-h-48 overflow-auto z-50">
                <div className="text-xs font-mono">
                  <div>Selected Agent: {selectedAgent}</div>
                  <div>Messages Count: {messages.length}</div>
                  <div>Last Message Role: {messages[messages.length - 1]?.role}</div>
                  <div>Last Message Preview: {messages[messages.length - 1]?.content?.substring(0, 50)}...</div>
                </div>
              </div>
            )}

            {/* Input Form */}
            <div className="bg-white border-t p-4">
              <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex gap-4">
                <input
                  type="text"
                  value={input}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
                  placeholder={`Ask the ${agentConfig[selectedAgent].name} anything...`}
                  className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading}
                  className={`bg-${agentConfig[selectedAgent].color}-500 text-white rounded-lg px-4 py-2 
                    hover:bg-${agentConfig[selectedAgent].color}-600 focus:outline-none 
                    focus:ring-2 focus:ring-${agentConfig[selectedAgent].color}-500 disabled:opacity-50`}
                >
                  <PaperAirplaneIcon className="h-5 w-5" />
                </button>
              </form>
            </div>
          </>
        ) : (
          // Welcome screen when no agent is selected
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Select an Engineering Agent
              </h2>
              <p className="text-gray-500">
                Choose an agent from the sidebar to start a conversation
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App 