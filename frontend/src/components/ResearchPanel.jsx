import { useState } from 'react'
import { Search, Loader2, Download, CheckCircle, XCircle, Sparkles, Brain } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'

const apiUrl = import.meta.env.VITE_API_URL || ''

export default function ResearchPanel() {
  const [query, setQuery] = useState('')
  const [isResearching, setIsResearching] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState(null)

  const handleStartResearch = async () => {
    if (!query.trim()) return

    setIsResearching(true)
    setError(null)
    setReport(null)

    try {
      const response = await fetch(`${apiUrl}/api/research/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query.trim(),
          max_iterations: 15,
          min_search_results: 8
        })
      })

      if (!response.ok) {
        throw new Error('Research request failed')
      }

      const data = await response.json()
      setReport(data.document_content)

    } catch (err) {
      setError(err.message || 'Research failed')
    } finally {
      setIsResearching(false)
    }
  }

  const handleDownloadReport = () => {
    if (!report) return

    const blob = new Blob([report], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `research_report_${Date.now()}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }



  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-4xl font-bold mb-2">
          <span className="bg-gradient-to-r from-accent-600 to-primary-600 bg-clip-text text-transparent">
            Deep Research Agent
          </span>
        </h2>
        <p className="text-neutral-600 dark:text-neutral-400 text-lg">
          AI-powered comprehensive research with detailed markdown reports
        </p>
      </div>

      {/* Search Input */}
      {!report && (
        <div className="bg-white dark:bg-neutral-800 rounded-2xl border border-neutral-200 dark:border-neutral-700 p-8 shadow-soft">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-accent-600 dark:text-accent-400" />
            <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100">
              What would you like to research?
            </h3>
          </div>

          <div className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !isResearching && handleStartResearch()}
              placeholder="e.g., How to build a ReAct agent using LangGraph?"
              className="flex-1 px-5 py-4 border-2 border-neutral-300 dark:border-neutral-600 rounded-2xl focus:outline-none focus:ring-2 focus:ring-accent-500 dark:focus:ring-accent-400 focus:border-accent-500 dark:focus:border-accent-400 transition-all duration-200 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 placeholder:text-neutral-400 dark:placeholder:text-neutral-500 shadow-soft"
              disabled={isResearching}
            />
            <button
              onClick={handleStartResearch}
              disabled={!query.trim() || isResearching}
              className="btn-primary px-8 rounded-2xl flex-shrink-0"
            >
              {isResearching ? (
                <Loader2 className="w-6 h-6 animate-spin" strokeWidth={2.5} />
              ) : (
                <>
                  <Search className="w-6 h-6" strokeWidth={2.5} />
                  Start Research
                </>
              )}
            </button>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-300 dark:border-red-700 rounded-xl flex items-start gap-3"
            >
              <XCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-red-900 dark:text-red-200 text-sm">Research Failed</p>
                <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
              </div>
            </motion.div>
          )}
        </div>
      )}

      {/* Research Progress */}
      <AnimatePresence>
        {isResearching && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-white dark:bg-neutral-800 rounded-2xl border border-neutral-200 dark:border-neutral-700 p-8 shadow-soft"
          >
            <div className="flex flex-col items-center justify-center py-8">
              <div className="relative mb-8">
                <div className="w-24 h-24 bg-gradient-to-br from-accent-500 via-primary-500 to-accent-600 rounded-3xl flex items-center justify-center shadow-xl animate-pulse">
                  <Brain className="w-12 h-12 text-white" strokeWidth={2.5} />
                </div>
                <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-white dark:bg-neutral-800 rounded-2xl shadow-large flex items-center justify-center border-2 border-accent-500 dark:border-accent-400">
                  <Loader2 className="w-6 h-6 text-accent-600 dark:text-accent-400 animate-spin" strokeWidth={2.5} />
                </div>
              </div>

              <h3 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
                Conducting Deep Research
              </h3>

              <p className="text-neutral-600 dark:text-neutral-400 mb-6 text-center max-w-md">
                Our AI agent is analyzing multiple sources and generating a comprehensive report
              </p>

              <div className="flex items-center gap-2 mt-4">
                <div className="w-2 h-2 bg-accent-500 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-accent-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Research Report */}
      <AnimatePresence>
        {report && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Report Header */}
            <div className="bg-white dark:bg-neutral-800 rounded-2xl border border-neutral-200 dark:border-neutral-700 p-6 shadow-soft flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-success-500 to-success-600 rounded-2xl flex items-center justify-center shadow-medium">
                  <CheckCircle className="w-7 h-7 text-white" strokeWidth={2.5} />
                </div>
                <div>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 font-semibold uppercase tracking-wider mb-1">
                    Research Completed
                  </p>
                  <p className="font-bold text-neutral-900 dark:text-neutral-100 text-lg">
                    Comprehensive Report Generated
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <button onClick={() => { setReport(null); setQuery(''); }} className="btn-ghost">
                  New Research
                </button>
                <button onClick={handleDownloadReport} className="btn-primary">
                  <Download className="w-5 h-5" />
                  Download Report
                </button>
              </div>
            </div>

            {/* Report Content */}
            <div className="bg-white dark:bg-neutral-800 rounded-2xl border border-neutral-200 dark:border-neutral-700 p-8 shadow-soft">
              <div className="markdown-content prose prose-neutral dark:prose-invert max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {report}
                </ReactMarkdown>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
