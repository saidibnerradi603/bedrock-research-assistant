import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, User, Bot, Sparkles, ChevronDown, ChevronUp, FileText } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'

function CitationCard({ source, index }) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="border border-neutral-200 dark:border-neutral-700 rounded-lg overflow-hidden bg-neutral-50 dark:bg-neutral-800/50 mb-2">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-neutral-100 dark:hover:bg-neutral-700/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-primary-600 dark:text-primary-400" />
          <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
            Source {index + 1}
          </span>
          {source.metadata?.source && (
            <span className="text-xs text-neutral-500 dark:text-neutral-500 truncate max-w-[200px]">
              {source.metadata.source.split('/').pop()}
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-neutral-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-neutral-500" />
        )}
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 py-3 border-t border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-800">
              <div className="prose prose-sm max-w-none dark:prose-invert text-neutral-600 dark:text-neutral-400">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {source.content}
                </ReactMarkdown>
              </div>
              {source.metadata && (
                <div className="mt-3 pt-3 border-t border-neutral-200 dark:border-neutral-700 space-y-1">
                  {source.metadata.chunk_index !== undefined && (
                    <p className="text-xs text-neutral-500 dark:text-neutral-500">
                      <span className="font-medium">Chunk:</span> {source.metadata.chunk_index}
                    </p>
                  )}
                  {source.metadata.source && (
                    <p className="text-xs text-neutral-500 dark:text-neutral-500 break-all">
                      <span className="font-medium">Source:</span> {source.metadata.source}
                    </p>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function ChatPanel({ paperId }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const messagesContainerRef = useRef(null)
  const abortControllerRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = { role: 'user', content: input }
    const question = input
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch('http://localhost:8000/api/chat/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          paper_id: paperId,
          question: question,
          top_k: 15
        }),
        signal: abortControllerRef.current.signal
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      // Read the entire response as text
      const responseText = await response.text()

      // Parse the JSON response
      let parsedResponse
      try {
        parsedResponse = JSON.parse(responseText)
      } catch (parseError) {
        console.error('Failed to parse JSON:', parseError)
        throw new Error('Invalid response format')
      }

      // Extract the answer and sources
      const assistantMessage = {
        role: 'assistant',
        content: parsedResponse.answer || 'No answer provided',
        sources: parsedResponse.source_documents || []
      }

      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Request was cancelled')
      } else {
        console.error('Error:', error)
        const errorMessage = {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          isError: true,
          sources: []
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } finally {
      setIsLoading(false)
      abortControllerRef.current = null
    }
  }

  return (
    <div className="flex flex-col h-[600px]">
      {/* Messages Area */}
      <div ref={messagesContainerRef} className="flex-1 overflow-y-auto mb-6 space-y-5 pr-2 scroll-smooth">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-lg">
              <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-primary-500 via-brand-500 to-primary-600 rounded-3xl flex items-center justify-center shadow-large">
                <Sparkles className="w-10 h-10 text-white" strokeWidth={2.5} />
              </div>
              <h3 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
                Ask me anything about your paper
              </h3>
              <p className="text-neutral-600 dark:text-neutral-400 mb-8 text-lg">
                I can help you understand key concepts, methodologies, results, and more.
              </p>
              <div className="grid grid-cols-1 gap-3 text-left">
                {[
                  'What is the main contribution?',
                  'Explain the methodology',
                  'What are the key findings?',
                  'What are the limitations?'
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(suggestion)}
                    className="p-4 bg-gradient-to-r from-neutral-50 to-primary-50/30 dark:from-neutral-800 dark:to-primary-900/20 hover:from-primary-50 hover:to-brand-50 dark:hover:from-primary-900/30 dark:hover:to-brand-900/30 border border-neutral-200 dark:border-neutral-700 hover:border-primary-300 dark:hover:border-primary-600 rounded-xl text-sm text-neutral-700 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-neutral-100 transition-all duration-200 text-left font-medium shadow-soft hover:shadow-medium"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((message, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.role === 'assistant' && (
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 via-brand-500 to-primary-600 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-medium">
                <Bot className="w-6 h-6 text-white" strokeWidth={2.5} />
              </div>
            )}

            <div className={`
              max-w-[75%] rounded-2xl shadow-soft
              ${message.role === 'user'
                ? 'bg-gradient-to-br from-primary-500 via-brand-500 to-primary-600 text-white p-5'
                : message.isError
                  ? 'bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/30 dark:to-red-800/30 border border-red-300 dark:border-red-700 p-5'
                  : 'bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700'
              }
            `}>
              {message.role === 'user' ? (
                <p className="text-white font-medium">{message.content}</p>
              ) : (
                <div>
                  <div className="p-5 markdown-content prose prose-neutral prose-sm max-w-none dark:prose-invert">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkMath]}
                      rehypePlugins={[rehypeKatex]}
                    >
                      {message.content}
                    </ReactMarkdown>
                  </div>

                  {message.sources && message.sources.length > 0 && (
                    <div className="px-5 pb-5">
                      <div className="pt-4 border-t border-neutral-200 dark:border-neutral-700">
                        <h4 className="text-sm font-semibold text-neutral-700 dark:text-neutral-300 mb-3 flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          Sources ({message.sources.length})
                        </h4>
                        {message.sources.map((source, sourceIdx) => (
                          <CitationCard
                            key={sourceIdx}
                            source={source}
                            index={sourceIdx}
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {message.role === 'user' && (
              <div className="w-10 h-10 bg-gradient-to-br from-neutral-200 to-neutral-300 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-soft">
                <User className="w-6 h-6 text-neutral-700" strokeWidth={2.5} />
              </div>
            )}
          </motion.div>
        ))}

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-4"
          >
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 via-brand-500 to-primary-600 rounded-2xl flex items-center justify-center shadow-medium">
              <Bot className="w-6 h-6 text-white" strokeWidth={2.5} />
            </div>
            <div className="bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-2xl p-5 shadow-soft">
              <div className="flex items-center gap-2">
                <Loader2 className="w-5 h-5 text-primary-600 dark:text-primary-400 animate-spin" strokeWidth={2.5} />
                <span className="text-sm text-neutral-600 dark:text-neutral-400 font-medium">Thinking...</span>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area - Fixed at bottom */}
      <div className="flex gap-3 flex-shrink-0">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSubmit(e)
            }
          }}
          placeholder="Ask a question about your paper..."
          className="flex-1 px-5 py-4 border-2 border-neutral-300 dark:border-neutral-600 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 focus:border-primary-500 dark:focus:border-primary-400 transition-all duration-200 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 placeholder:text-neutral-400 dark:placeholder:text-neutral-500 shadow-soft"
          disabled={isLoading}
        />
        <button
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading}
          className="btn-primary px-8 rounded-2xl flex-shrink-0"
        >
          {isLoading ? (
            <Loader2 className="w-6 h-6 animate-spin" strokeWidth={2.5} />
          ) : (
            <Send className="w-6 h-6" strokeWidth={2.5} />
          )}
        </button>
      </div>
    </div>
  )
}