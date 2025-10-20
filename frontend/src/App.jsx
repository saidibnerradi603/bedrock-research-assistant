import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FileText, Upload } from 'lucide-react'
import Header from './components/Header'
import UploadArea from './components/UploadArea'
import FeatureTabs from './components/FeatureTabs'
import ChatPanel from './components/ChatPanel'
import SummaryPanel from './components/SummaryPanel'
import QuizPanel from './components/QuizPanel'
import MindmapPanel from './components/MindmapPanel'
import ResearchPanel from './components/ResearchPanel'

function App() {
  const [paperId, setPaperId] = useState(null)
  const [activeTab, setActiveTab] = useState('chat')
  const [uploadedFileName, setUploadedFileName] = useState('')

  const handleUploadSuccess = (id, fileName) => {
    setPaperId(id)
    setUploadedFileName(fileName)
    setActiveTab('chat')
  }

  const handleReset = () => {
    setPaperId(null)
    setUploadedFileName('')
    setActiveTab('chat')
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-neutral-900 transition-colors duration-300">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <AnimatePresence mode="wait">
          {!paperId ? (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <UploadArea onUploadSuccess={handleUploadSuccess} />
            </motion.div>
          ) : (
            <motion.div
              key="features"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              {/* Paper Info Bar */}
              <div className="glass-card p-6 flex items-center justify-between shadow-soft">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-primary-600 dark:bg-primary-500 rounded-2xl flex items-center justify-center shadow-medium">
                    <FileText className="w-7 h-7 text-white" strokeWidth={2.5} />
                  </div>
                  <div>
                    <p className="text-xs text-neutral-500 dark:text-neutral-400 font-semibold uppercase tracking-wider mb-1">Current Paper</p>
                    <p className="font-bold text-neutral-900 dark:text-neutral-100 truncate max-w-md text-lg">{uploadedFileName}</p>
                  </div>
                </div>
                <button
                  onClick={handleReset}
                  className="btn-secondary"
                >
                  <Upload className="w-5 h-5" />
                  Upload New
                </button>
              </div>

              {/* Feature Tabs */}
              <FeatureTabs activeTab={activeTab} setActiveTab={setActiveTab} />

              {/* Content Area */}
              <div className="glass-card p-8 min-h-[600px] shadow-soft bg-white dark:bg-neutral-800">
                <AnimatePresence mode="wait">
                  {activeTab === 'chat' && (
                    <motion.div
                      key={`chat-${paperId}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ChatPanel key={paperId} paperId={paperId} />
                    </motion.div>
                  )}
                  
                  {activeTab === 'summary' && (
                    <motion.div
                      key={`summary-${paperId}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <SummaryPanel key={paperId} paperId={paperId} />
                    </motion.div>
                  )}
                  
                  {activeTab === 'quiz' && (
                    <motion.div
                      key={`quiz-${paperId}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <QuizPanel key={paperId} paperId={paperId} />
                    </motion.div>
                  )}
                  
                  {activeTab === 'mindmap' && (
                    <motion.div
                      key={`mindmap-${paperId}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <MindmapPanel key={paperId} paperId={paperId} />
                    </motion.div>
                  )}
                  
                  {activeTab === 'research' && (
                    <motion.div
                      key="research"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ResearchPanel />
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App
