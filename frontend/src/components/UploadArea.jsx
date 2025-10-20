import { useState, useRef } from 'react'
import { Upload, FileText, Loader2, CheckCircle, AlertCircle, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import axios from 'axios'

const apiUrl = import.meta.env.VITE_API_URL || ''

export default function UploadArea({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [duplicateInfo, setDuplicateInfo] = useState(null)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) handleFile(file)
  }

  const handleFile = async (file) => {
    if (!file.type.includes('pdf')) {
      setError('Please upload a PDF file')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB')
      return
    }

    setError(null)
    setDuplicateInfo(null)
    setIsUploading(true)
    setUploadProgress(0)

    try {
      // Step 1: Upload and process PDF
      const formData = new FormData()
      formData.append('file', file)

      const uploadResponse = await axios.post(`${apiUrl}/api/papers/upload-and-process`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          setUploadProgress(progress)
        }
      })

      const { paper_id, message } = uploadResponse.data
      setIsUploading(false)

      // Check if this is a duplicate paper
      const isDuplicate = message && (
        message.includes('already processed') || 
        message.includes('already embedded')
      )

      if (isDuplicate) {
        // Paper already exists - check if it's embedded
        const isAlreadyEmbedded = message.includes('already embedded') || 
                                  message.includes('vectors in database')
        
        if (isAlreadyEmbedded) {
          // Paper is fully ready - no need to embed
          setDuplicateInfo({
            type: 'success',
            message: 'This paper has already been processed and is ready to use!',
            details: message
          })
          // Wait a moment to show the message, then proceed
          await new Promise(resolve => setTimeout(resolve, 2000))
          onUploadSuccess(paper_id, file.name)
          return
        } else {
          // Paper exists but not embedded yet
          setDuplicateInfo({
            type: 'info',
            message: 'This paper was previously uploaded. Completing the embedding process...',
            details: message
          })
        }
      }

      setIsProcessing(true)

      // Step 2: Embed and store (synchronous operation)
      const embedResponse = await axios.post(`${apiUrl}/api/papers/embed-store`, {
        paper_id
      })

      const { message: embedMessage } = embedResponse.data

      // Embedding complete
      setIsProcessing(false)
      
      // Check if embedding was already done or just completed
      if (embedMessage && embedMessage.includes('already embedded')) {
        setDuplicateInfo({
          type: 'success',
          message: 'Paper is already embedded and ready to use!',
          details: embedMessage
        })
        await new Promise(resolve => setTimeout(resolve, 1500))
      }
      
      onUploadSuccess(paper_id, file.name)

    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
      setIsUploading(false)
      setIsProcessing(false)
      setDuplicateInfo(null)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-10"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 dark:bg-primary-900/30 border border-primary-200 dark:border-primary-700 rounded-full mb-6">
          <Sparkles className="w-4 h-4 text-primary-600 dark:text-primary-400" />
          <span className="text-sm font-semibold text-primary-700 dark:text-primary-300">Powered by AI</span>
        </div>
        <h2 className="text-5xl font-bold mb-4 text-neutral-900 dark:text-neutral-100">
          Analyze Your Research Paper
        </h2>
        <p className="text-xl text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto">
          Upload a PDF to unlock AI-powered insights, comprehensive summaries, and interactive features
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-10"
      >
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-3 border-dashed rounded-2xl p-16 text-center transition-all duration-300
            ${isDragging 
              ? 'border-primary-500 dark:border-primary-400 bg-primary-50 dark:bg-primary-900/20 scale-[1.02]' 
              : 'border-neutral-300 dark:border-neutral-600 hover:border-primary-400 dark:hover:border-primary-500 hover:bg-neutral-50 dark:hover:bg-neutral-800'
            }
            ${(isUploading || isProcessing) ? 'pointer-events-none opacity-60' : 'cursor-pointer'}
          `}
          onClick={() => !isUploading && !isProcessing && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
          />

          {!isUploading && !isProcessing && (
            <>
              <div className="w-24 h-24 mx-auto mb-6 bg-primary-600 dark:bg-primary-500 rounded-3xl flex items-center justify-center shadow-large">
                <Upload className="w-12 h-12 text-white" strokeWidth={2.5} />
              </div>
              <h3 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
                Drop your PDF here
              </h3>
              <p className="text-neutral-600 dark:text-neutral-400 mb-8 text-lg">
                or click to browse from your computer
              </p>
              <div className="flex justify-center">
                <button className="btn-primary text-lg px-8 py-4">
                  <FileText className="w-6 h-6" />
                  Select PDF File
                </button>
              </div>
              <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-6">
                Maximum file size: 5MB • Supported format: PDF
              </p>
            </>
          )}

          {isUploading && (
            <div className="space-y-6">
              <div className="w-24 h-24 mx-auto bg-primary-600 dark:bg-primary-500 rounded-3xl flex items-center justify-center animate-pulse">
                <Loader2 className="w-12 h-12 text-white animate-spin" strokeWidth={2.5} />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
                  Uploading & Processing
                </h3>
                <p className="text-neutral-600 dark:text-neutral-400 mb-6 text-lg">
                  Extracting text and structure from your PDF
                </p>
                <div className="w-full max-w-md mx-auto bg-neutral-200 dark:bg-neutral-700 rounded-full h-4 overflow-hidden shadow-inner-soft">
                  <motion.div
                    className="h-full bg-primary-600 dark:bg-primary-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${uploadProgress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
                <p className="text-lg font-semibold text-primary-600 dark:text-primary-400 mt-3">{uploadProgress}%</p>
              </div>
            </div>
          )}

          {isProcessing && (
            <div className="space-y-6">
              <div className="w-24 h-24 mx-auto bg-brand-600 dark:bg-brand-500 rounded-3xl flex items-center justify-center animate-pulse">
                <Loader2 className="w-12 h-12 text-white animate-spin" strokeWidth={2.5} />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
                  Creating Embeddings
                </h3>
                <p className="text-neutral-600 dark:text-neutral-400 text-lg mb-6">
                  Generating vector embeddings for semantic search
                </p>
                <div className="flex items-center justify-center gap-3">
                  <div className="w-3 h-3 bg-primary-500 dark:bg-primary-400 rounded-full animate-bounce" />
                  <div className="w-3 h-3 bg-brand-500 dark:bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                  <div className="w-3 h-3 bg-primary-500 dark:bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                </div>
              </div>
            </div>
          )}
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 p-5 bg-red-50 dark:bg-red-900/20 border border-red-300 dark:border-red-700 rounded-xl flex items-start gap-4 shadow-soft"
          >
            <div className="w-10 h-10 bg-red-500 dark:bg-red-600 rounded-xl flex items-center justify-center flex-shrink-0">
              <AlertCircle className="w-5 h-5 text-white" strokeWidth={2.5} />
            </div>
            <div className="flex-1">
              <p className="font-bold text-red-900 dark:text-red-200 mb-1">Upload Error</p>
              <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            </div>
          </motion.div>
        )}

        {duplicateInfo && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`mt-6 p-5 rounded-xl flex items-start gap-4 shadow-soft ${
              duplicateInfo.type === 'success' 
                ? 'bg-success-50 dark:bg-success-900/20 border border-success-300 dark:border-success-700' 
                : 'bg-brand-50 dark:bg-brand-900/20 border border-brand-300 dark:border-brand-700'
            }`}
          >
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
              duplicateInfo.type === 'success' ? 'bg-success-500 dark:bg-success-600' : 'bg-brand-500 dark:bg-brand-600'
            }`}>
              <CheckCircle className="w-5 h-5 text-white" strokeWidth={2.5} />
            </div>
            <div className="flex-1">
              <p className={`font-bold mb-1 ${
                duplicateInfo.type === 'success' ? 'text-success-900 dark:text-success-200' : 'text-brand-900 dark:text-brand-200'
              }`}>
                {duplicateInfo.type === 'success' ? 'Paper Already Processed' : 'Duplicate Detected'}
              </p>
              <p className={`text-sm ${
                duplicateInfo.type === 'success' ? 'text-success-700 dark:text-success-300' : 'text-brand-700 dark:text-brand-300'
              }`}>
                {duplicateInfo.message}
              </p>
              {duplicateInfo.details && (
                <p className={`text-xs mt-2 ${
                  duplicateInfo.type === 'success' ? 'text-success-600 dark:text-success-400' : 'text-brand-600 dark:text-brand-400'
                }`}>
                  {duplicateInfo.details}
                </p>
              )}
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}
