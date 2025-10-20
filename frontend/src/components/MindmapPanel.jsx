import { useState, useEffect } from 'react'
import { Loader2, Brain, ExternalLink } from 'lucide-react'
import axios from 'axios'

const apiUrl = import.meta.env.VITE_API_URL || ''

export default function MindmapPanel({ paperId }) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [mindmapUrl, setMindmapUrl] = useState(null)

  useEffect(() => {
    if (paperId) {
      fetchMindmap()
    }
    
    // Cleanup blob URL on unmount
    return () => {
      if (mindmapUrl) {
        URL.revokeObjectURL(mindmapUrl)
      }
    }
  }, [paperId])

  const fetchMindmap = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
     const response = await axios.get(`${apiUrl}/api/papers/${paperId}/mindmap`, {
        responseType: 'text'
      })
      
      // Create blob URL from HTML content
      const blob = new Blob([response.data], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      setMindmapUrl(url)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate mindmap')
    } finally {
      setIsLoading(false)
    }
  }

  const openInNewTab = () => {
    if (mindmapUrl) {
      window.open(mindmapUrl, '_blank')
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px]">
        <div className="relative mb-8">
          <div className="w-24 h-24 bg-gradient-to-br from-accent-500 to-primary-500 rounded-3xl flex items-center justify-center shadow-xl animate-pulse">
            <Brain className="w-12 h-12 text-white" strokeWidth={2.5} />
          </div>
          <div className="absolute -bottom-3 -right-3 w-12 h-12 bg-white rounded-2xl shadow-large flex items-center justify-center">
            <Loader2 className="w-7 h-7 text-accent-600 animate-spin" strokeWidth={2.5} />
          </div>
        </div>
        <h3 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
          Generating Mind Map
        </h3>
        <p className="text-neutral-600 dark:text-neutral-400 text-lg">
          Creating interactive visualization
        </p>
        <div className="flex items-center gap-2 mt-6">
          <div className="w-2 h-2 bg-accent-500 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
          <div className="w-2 h-2 bg-accent-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px]">
        <div className="w-24 h-24 bg-gradient-to-br from-red-100 to-red-200 rounded-3xl flex items-center justify-center mb-8 shadow-large">
          <Brain className="w-12 h-12 text-red-600" strokeWidth={2.5} />
        </div>
        <h3 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
          Failed to Generate Mind Map
        </h3>
        <p className="text-neutral-600 dark:text-neutral-400 mb-8 text-lg">{error}</p>
        <button onClick={fetchMindmap} className="btn-primary text-lg px-8">
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-4xl font-bold mb-2">
            <span className="bg-gradient-to-r from-accent-600 to-primary-600 bg-clip-text text-transparent">
              Interactive Mind Map
            </span>
          </h2>
          <p className="text-neutral-600 dark:text-neutral-400 text-lg">
            Visual representation of paper structure and concepts
          </p>
        </div>
        <button onClick={openInNewTab} className="btn-secondary">
          <ExternalLink className="w-5 h-5" />
          Open in New Tab
        </button>
      </div>

      <div className="bg-white dark:bg-neutral-800 rounded-2xl border border-neutral-200 dark:border-neutral-700 overflow-hidden shadow-soft">
        {mindmapUrl && (
          <iframe
            src={mindmapUrl}
            className="w-full h-[600px]"
            title="Research Paper Mind Map"
          />
        )}
      </div>

      <div className="bg-gradient-to-r from-brand-50 to-brand-100 dark:from-brand-900/30 dark:to-brand-800/30 border border-brand-300 dark:border-brand-700 rounded-xl p-5 shadow-soft">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-brand-500 dark:bg-brand-600 rounded-lg flex items-center justify-center flex-shrink-0">
            <Brain className="w-5 h-5 text-white" strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-sm font-bold text-brand-900 dark:text-brand-200 mb-1">
              Interactive Controls
            </p>
            <p className="text-sm text-brand-800 dark:text-brand-300">
              Click and drag to pan, scroll to zoom, and click nodes to expand/collapse sections.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
