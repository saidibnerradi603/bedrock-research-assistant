import { motion } from 'framer-motion'
import { BookOpen, Brain } from 'lucide-react'
import ThemeToggle from './ThemeToggle'

export default function Header() {
  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="bg-white dark:bg-neutral-800 border-b border-neutral-200 dark:border-neutral-700 sticky top-0 z-50 shadow-soft"
    >
      <div className="container mx-auto px-6 py-4 max-w-7xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-primary-600 dark:bg-primary-500 rounded-2xl flex items-center justify-center shadow-medium">
              <BookOpen className="w-6 h-6 text-white" strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-xl font-bold text-primary-600 dark:text-primary-400">
                ResearchAI
              </h1>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 font-medium">AI-Powered Research Analysis</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-success-50 dark:bg-success-900/30 border border-success-200 dark:border-success-700 rounded-xl">
              <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
              <span className="text-xs font-semibold text-success-700 dark:text-success-400">Online</span>
            </div>
            <div className="hidden lg:flex items-center gap-2 px-4 py-2 bg-brand-50 dark:bg-brand-900/30 border border-brand-200 dark:border-brand-700 rounded-xl">
              <Brain className="w-4 h-4 text-brand-600 dark:text-brand-400" />
              <span className="text-xs font-semibold text-brand-700 dark:text-brand-400">AWS Bedrock</span>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </motion.header>
  )
}
