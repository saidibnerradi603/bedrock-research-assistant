import { useState, useEffect } from 'react'
import { Loader2, FileText, ChevronDown, ChevronUp, BookOpen, Lightbulb, FlaskConical, Target, TrendingUp, AlertTriangle, Rocket, Layers } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'

const sections = [
  { key: 'summary', label: 'Executive Summary', icon: FileText, color: 'bg-brand-rand-500 to-brand-600', bg: 'from-brand-50 to-brand-100', border: 'border-brand-200' },
  { key: 'background', label: 'Background', icon: BookOpen, gradient: 'from-primary-500 to-primary-600', bg: 'from-primary-50 to-primary-100', border: 'border-primary-200' },
  { key: 'problem', label: 'Research Problem', icon: Target, gradient: 'from-red-500 to-red-600', bg: 'from-red-50 to-red-100', border: 'border-red-200' },
  { key: 'methods', label: 'Methodology', icon: FlaskConical, gradient: 'from-success-500 to-success-600', bg: 'from-success-50 to-success-100', border: 'border-success-200' },
  { key: 'experiments', label: 'Experiments', icon: Layers, gradient: 'from-teal-500 to-teal-600', bg: 'from-teal-50 to-teal-100', border: 'border-teal-200' },
  { key: 'results', label: 'Results & Findings', icon: TrendingUp, gradient: 'from-indigo-500 to-indigo-600', bg: 'from-indigo-50 to-indigo-100', border: 'border-indigo-200' },
  { key: 'limitations', label: 'Limitations', icon: AlertTriangle, gradient: 'from-accent-500 to-accent-600', bg: 'from-accent-50 to-accent-100', border: 'border-accent-200' },
  { key: 'implications', label: 'Implications', icon: Lightbulb, gradient: 'from-yellow-500 to-yellow-600', bg: 'from-yellow-50 to-yellow-100', border: 'border-yellow-200' },
  { key: 'future_work', label: 'Future Work', icon: Rocket, gradient: 'from-pink-500 to-pink-600', bg: 'from-pink-50 to-pink-100', border: 'border-pink-200' },
]

function SectionCard({ section, content, isExpanded, onToggle }) {
  const Icon = section.icon
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-neutral-800 rounded-2xl border border-neutral-200 dark:border-neutral-700 overflow-hidden shadow-soft hove00"
    >
      <button
        onClick={onToggle}
        className="w-full p-6 flex items-center justify-between hover:bg-gradient-to-r hover:from-neutral-50 dark:hover:from-neutral-700/50 hover:to-transparent transition-all duration-300 group"
      >
        <div className="flex items-center gap-5">
          <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${section.gradient} flex items-center justify-center shadow-medium group-hover:scale-110 transition-transform duration-300`}>
            <Icon className="w-7 h-7 text-white" strokeWidth={2.5} />
          </div>
          <div className="text-left">
            <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">{section.label}</h3>
            <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1 font-medium">Click to {isExpanded ? 'collapse' : 'expand'}</p>
          </div>
        </div>
        <div className={`w-12 h-12 rounded-xl bg-neutral-100 dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 flex items-center justify-center transition-all duration-300 ${isExpanded ? 'rotate-180 scale-110' : 'group-hover:scale-110'}`}>
          <ChevronDown className="w-6 h-6 text-neutral-700 dark:text-neutral-300" strokeWidth={2.5} />
        </div>
      </button>
      
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-8 pt-6 border-t border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900">
              <div className="markdown-content prose prose-neutral dark:prose-invert max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                >
                  {content}
                </ReactMarkdown>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function SummaryPanel({ paperId }) {
  const [summary, setSummary] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [expandedSections, setExpandedSections] = useState(new Set(['summary']))

  useEffect(() => {
    if (paperId) {
      fetchSummary()
    }
  }, [paperId])

  const fetchSummary = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await axios.get(`/api/papers/${paperId}/summary`)
      setSummary(response.data.summary)
      setExpandedSections(new Set(['summary']))
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate summary')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleSection = (key) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev)
      if (newSet.has(key)) {
        newSet.delete(key)
      } else {
        newSet.add(key)
      }
      return newSet
    })
  }

  const expandAll = () => {
    setExpandedSections(new Set(sections.map(s => s.key)))
  }

  const collapseAll = () => {
    setExpandedSections(new Set())
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px]">
        <div className="relative mb-8">
          <div className="w-24 h-24 bg-gradient-to-br from-primary-500 via-brand-500 to-primary-600 rounded-3xl flex items-center justify-center shadow-xl animate-pulse">
            <FileText className="w-12 h-12 text-white" strokeWidth={2.5} />
          </div>
          <div className="absolute -bottom-3 -right-3 w-12 h-12 bg-white rounded-2xl shadow-large flex items-center justify-center">
            <Loader2 className="w-7 h-7 text-primary-600 animate-spin" strokeWidth={2.5} />
          </div>
        </div>
        <h3 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
          Generating Comprehensive Summary
        </h3>
        <p className="text-neutral-600 dark:text-neutral-400 text-center max-w-lg text-lg">
          Our AI is analyzing your paper and creating a detailed summary. This may take 30-60 seconds.
        </p>
        <div className="flex items-center gap-2 mt-6">
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-brand-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
          <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px]">
        <div className="w-24 h-24 bg-gradient-to-br from-red-100 to-red-200 rounded-3xl flex items-center justify-center mb-8 shadow-large">
          <FileText className="w-12 h-12 text-red-600" strokeWidth={2.5} />
        </div>
        <h3 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
          Failed to Generate Summary
        </h3>
        <p className="text-neutral-600 dark:text-neutral-400 mb-8 text-center max-w-md text-lg">{error}</p>
        <button onClick={fetchSummary} className="btn-primary text-lg px-8">
          <Loader2 className="w-5 h-5" />
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
            <span className="bg-gradient-to-r from-primary-600 to-brand-600 bg-clip-text text-transparent">
              Paper Summary
            </span>
          </h2>
          <p className="text-neutral-600 dark:text-neutral-400 text-lg">Comprehensive AI-generated analysis with {sections.length} sections</p>
        </div>
        <div className="flex gap-3">
          <button onClick={expandAll} className="btn-ghost">
            <ChevronDown className="w-5 h-5" />
            Expand All
          </button>
          <button onClick={collapseAll} className="btn-ghost">
            <ChevronUp className="w-5 h-5" />
            Collapse All
          </button>
        </div>
      </div>

      <div className="space-y-5">
        {sections.map((section) => (
          <SectionCard
            key={section.key}
            section={section}
            content={summary?.[section.key] || ''}
            isExpanded={expandedSections.has(section.key)}
            onToggle={() => toggleSection(section.key)}
          />
        ))}
      </div>
    </div>
  )
}
