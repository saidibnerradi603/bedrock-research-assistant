import { MessageSquare, FileText, Network, HelpCircle, Search } from 'lucide-react'
import { motion } from 'framer-motion'

const tabs = [
  { id: 'chat', label: 'AI Chat', icon: MessageSquare, description: 'Ask questions', color: 'brand' },
  { id: 'summary', label: 'Summary', icon: FileText, description: 'Deep analysis', color: 'primary' },
  { id: 'quiz', label: 'Quiz', icon: HelpCircle, description: 'Test knowledge', color: 'success' },
  { id: 'mindmap', label: 'Mind Map', icon: Network, description: 'Visual structure', color: 'accent' },
  { id: 'research', label: 'Research', icon: Search, description: 'Deep research', color: 'accent' },
]

const colorClasses = {
  brand: {
    active: 'bg-brand-600 dark:bg-brand-500',
    inactive: 'bg-brand-50 dark:bg-brand-900/30',
    hover: 'hover:bg-brand-100 dark:hover:bg-brand-900/40',
    icon: 'text-brand-700 dark:text-brand-300'
  },
  primary: {
    active: 'bg-primary-600 dark:bg-primary-500',
    inactive: 'bg-primary-50 dark:bg-primary-900/30',
    hover: 'hover:bg-primary-100 dark:hover:bg-primary-900/40',
    icon: 'text-primary-700 dark:text-primary-300'
  },
  success: {
    active: 'bg-success-600 dark:bg-success-500',
    inactive: 'bg-success-50 dark:bg-success-900/30',
    hover: 'hover:bg-success-100 dark:hover:bg-success-900/40',
    icon: 'text-success-700 dark:text-success-300'
  },
  accent: {
    active: 'bg-accent-600 dark:bg-accent-500',
    inactive: 'bg-accent-50 dark:bg-accent-900/30',
    hover: 'hover:bg-accent-100 dark:hover:bg-accent-900/40',
    icon: 'text-accent-700 dark:text-accent-300'
  }
}

export default function FeatureTabs({ activeTab, setActiveTab }) {
  return (
    <div className="glass-card p-3 shadow-soft">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = activeTab === tab.id
          const colors = colorClasses[tab.color]
          
          return (
            <motion.button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              whileHover={{ scale: isActive ? 1 : 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`
                relative p-5 rounded-2xl transition-all duration-300 group
                ${isActive 
                  ? `${colors.active} text-white shadow-large` 
                  : `bg-white dark:bg-neutral-700 ${colors.hover} text-neutral-700 dark:text-neutral-200 hover:shadow-medium border border-neutral-200 dark:border-neutral-600`
                }
              `}
            >
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute inset-0 bg-white/10 dark:bg-white/5 rounded-2xl"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
              <div className="relative flex flex-col items-center gap-3">
                <div className={`
                  w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-300
                  ${isActive 
                    ? 'bg-white/20 dark:bg-white/10 shadow-medium' 
                    : `${colors.inactive} group-hover:scale-110`
                  }
                `}>
                  <Icon className={`w-7 h-7 ${isActive ? 'text-white' : colors.icon}`} strokeWidth={2.5} />
                </div>
                <div className="text-center">
                  <p className={`font-bold text-sm mb-0.5 ${isActive ? 'text-white' : 'text-neutral-900 dark:text-neutral-100'}`}>
                    {tab.label}
                  </p>
                  <p className={`text-xs ${isActive ? 'text-white/90' : 'text-neutral-500 dark:text-neutral-400'}`}>
                    {tab.description}
                  </p>
                </div>
              </div>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}
