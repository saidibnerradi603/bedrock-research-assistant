import { useState, useEffect } from 'react'
import { Loader2, CheckCircle, XCircle, HelpCircle, RotateCcw } from 'lucide-react'
import { motion } from 'framer-motion'
import axios from 'axios'

function QuizQuestion({ question, index, onAnswer, userAnswer, showResult }) {
  const optionLetters = ['A', 'B', 'C', 'D']
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="bg-white dark:bg-neutral-800 rounded-2xl border border-neutral-200 dark:border-neutral-700 p-7 shadow-soft hover:shadow-medium transition-all duration-300"
    >
      <div className="flex items-start gap-4 mb-6">
        <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-brand-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-medium">
          <span className="text-white font-bold text-lg">{question.id || index + 1}</span>
        </div>
        <h3 className="text-lg font-bold text-neutral-900 dark:text-neutral-100 flex-1 leading-relaxed">
          {question.question}
        </h3>
      </div>

      <div className="space-y-3 ml-14">
        {optionLetters.map((letter) => {
          const isSelected = userAnswer === letter
          const isCorrect = question.correct_answer === letter
          const showCorrect = showResult && isCorrect
          const showWrong = showResult && isSelected && !isCorrect

          return (
            <button
              key={letter}
              onClick={() => !showResult && onAnswer(index, letter)}
              disabled={showResult}
              className={`
                w-full p-5 rounded-xl text-left transition-all duration-200 flex items-center gap-4 font-medium
                ${!showResult && 'hover:scale-[1.02] cursor-pointer'}
                ${isSelected && !showResult && 'bg-gradient-to-r from-primary-50 to-brand-50 dark:from-primary-900/30 dark:to-brand-900/30 border-2 border-primary-500 dark:border-primary-400 shadow-medium'}
                ${!isSelected && !showResult && 'bg-neutral-50 dark:bg-neutral-700 border-2 border-neutral-200 dark:border-neutral-600 hover:border-neutral-300 dark:hover:border-neutral-500 hover:bg-neutral-100 dark:hover:bg-neutral-600'}
                ${showCorrect && 'bg-gradient-to-r from-success-50 to-success-100 dark:from-success-900/30 dark:to-success-800/30 border-2 border-success-500 dark:border-success-400 shadow-medium'}
                ${showWrong && 'bg-gradient-to-r from-red-50 to-red-100 dark:from-red-900/30 dark:to-red-800/30 border-2 border-red-500 dark:border-red-400 shadow-medium'}
                ${showResult && !isSelected && !isCorrect && 'opacity-40'}
                ${showResult && 'cursor-default'}
              `}
            >
              <div className={`
                w-10 h-10 rounded-xl flex items-center justify-center font-bold flex-shrink-0 text-lg transition-all duration-200
                ${isSelected && !showResult && 'bg-gradient-to-br from-primary-500 to-brand-500 text-white shadow-medium'}
                ${!isSelected && !showResult && 'bg-neutral-200 dark:bg-neutral-600 text-neutral-600 dark:text-neutral-300'}
                ${showCorrect && 'bg-gradient-to-br from-success-500 to-success-600 text-white shadow-medium'}
                ${showWrong && 'bg-gradient-to-br from-red-500 to-red-600 text-white shadow-medium'}
              `}>
                {showCorrect ? <CheckCircle className="w-6 h-6" strokeWidth={2.5} /> : 
                 showWrong ? <XCircle className="w-6 h-6" strokeWidth={2.5} /> : 
                 letter}
              </div>
              <span className="flex-1 text-neutral-800 dark:text-neutral-200">{question.options[letter]}</span>
            </button>
          )
        })}
      </div>

      {showResult && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-6 ml-14 p-5 bg-gradient-to-r from-brand-50 to-brand-100 dark:from-brand-900/30 dark:to-brand-800/30 border border-brand-300 dark:border-brand-700 rounded-xl shadow-soft"
        >
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 bg-brand-500 dark:bg-brand-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <CheckCircle className="w-5 h-5 text-white" strokeWidth={2.5} />
            </div>
            <div className="flex-1">
              <p className="text-sm font-bold text-brand-900 dark:text-brand-200 mb-2">
                Correct Answer: {question.correct_answer}
              </p>
              <p className="text-sm text-brand-800 dark:text-brand-300 leading-relaxed">{question.explanation}</p>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

export default function QuizPanel({ paperId }) {
  const [quiz, setQuiz] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [userAnswers, setUserAnswers] = useState({})
  const [showResults, setShowResults] = useState(false)
  const [score, setScore] = useState(0)

  useEffect(() => {
    if (paperId) {
      fetchQuiz()
    }
  }, [paperId])

  const fetchQuiz = async () => {
    setIsLoading(true)
    setError(null)
    setUserAnswers({})
    setShowResults(false)
    
    try {
      const response = await axios.get(`/api/papers/${paperId}/quiz?num_questions=10`)
      
      console.log("Quiz response:", response.data);
      
      // The backend returns: { paper_id, questions: [...], processing_time_seconds, message }
      if (!response.data || !Array.isArray(response.data.questions)) {
        throw new Error("Invalid quiz response format");
      }
      
      // Log first question to debug structure
      if (response.data.questions.length > 0) {
        console.log("First question structure:", JSON.stringify(response.data.questions[0], null, 2));
      }
      
      // Validate each question has the required fields with new schema
      const validQuestions = response.data.questions.every((q, idx) => {
        // Check if options is an object with A, B, C, D keys
        const hasValidOptions = q.options && 
          typeof q.options === 'object' &&
          'A' in q.options && 
          'B' in q.options && 
          'C' in q.options && 
          'D' in q.options;
        
        const isValid = q.question && 
          hasValidOptions &&
          q.correct_answer && 
          q.explanation;
        
        if (!isValid) {
          console.error(`Question ${idx + 1} validation failed:`, {
            hasQuestion: !!q.question,
            hasOptions: !!q.options,
            optionsType: typeof q.options,
            optionsKeys: q.options ? Object.keys(q.options) : [],
            hasValidOptions,
            hasCorrectAnswer: !!q.correct_answer,
            hasExplanation: !!q.explanation
          });
        }
        
        return isValid;
      });
      
      if (!validQuestions) {
        console.error("Some questions have invalid format");
        throw new Error("Quiz questions have invalid format");
      }
      
      setQuiz(response.data)
    } catch (err) {
      console.error("Quiz fetch error:", err);
      setError(err.response?.data?.detail || err.message || 'Failed to generate quiz')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAnswer = (questionIndex, answer) => {
    setUserAnswers(prev => ({
      ...prev,
      [questionIndex]: answer
    }))
  }

  const handleSubmit = () => {
    let correct = 0
    quiz.questions.forEach((q, idx) => {
      if (userAnswers[idx] === q.correct_answer) {
        correct++
      }
    })
    setScore(correct)
    setShowResults(true)
  }

  const handleReset = () => {
    setUserAnswers({})
    setShowResults(false)
    setScore(0)
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px]">
        <div className="relative mb-8">
          <div className="w-24 h-24 bg-gradient-to-br from-success-500 to-brand-500 rounded-3xl flex items-center justify-center shadow-xl animate-pulse">
            <HelpCircle className="w-12 h-12 text-white" strokeWidth={2.5} />
          </div>
          <div className="absolute -bottom-3 -right-3 w-12 h-12 bg-white rounded-2xl shadow-large flex items-center justify-center">
            <Loader2 className="w-7 h-7 text-success-600 animate-spin" strokeWidth={2.5} />
          </div>
        </div>
        <h3 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
          Generating Quiz Questions
        </h3>
        <p className="text-neutral-600 dark:text-neutral-400 text-lg">
          Creating 10 questions to test your understanding
        </p>
        <div className="flex items-center gap-2 mt-6">
          <div className="w-2 h-2 bg-success-500 rounded-full animate-bounce" />
          <div className="w-2 h-2 bg-brand-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
          <div className="w-2 h-2 bg-success-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-[600px]">
        <div className="w-24 h-24 bg-gradient-to-br from-red-100 to-red-200 rounded-3xl flex items-center justify-center mb-8 shadow-large">
          <HelpCircle className="w-12 h-12 text-red-600" strokeWidth={2.5} />
        </div>
        <h3 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-3">
          Failed to Generate Quiz
        </h3>
        <p className="text-neutral-600 dark:text-neutral-400 mb-8 text-lg">{error}</p>
        <button onClick={fetchQuiz} className="btn-primary text-lg px-8">
          Try Again
        </button>
      </div>
    )
  }

  const answeredCount = Object.keys(userAnswers).length
  const totalQuestions = quiz?.questions?.length || 0
  const canSubmit = answeredCount === totalQuestions && !showResults

  const getScoreColor = () => {
    const percentage = (score / totalQuestions) * 100
    if (percentage >= 80) return 'text-green-600'
    if (percentage >= 60) return 'text-blue-600'
    if (percentage >= 40) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreMessage = () => {
    const percentage = (score / totalQuestions) * 100
    if (percentage >= 90) return 'Excellent! 🎉'
    if (percentage >= 80) return 'Great job! 👏'
    if (percentage >= 70) return 'Good work! 👍'
    if (percentage >= 60) return 'Not bad! 📚'
    if (percentage >= 50) return 'Keep studying! 💪'
    return 'Review the material! 📖'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h2 className="text-4xl font-bold mb-2">
            <span className="bg-gradient-to-r from-success-600 to-brand-600 bg-clip-text text-transparent">
              Knowledge Quiz
            </span>
          </h2>
          <p className="text-neutral-600 dark:text-neutral-400 text-lg">
            Test your understanding of the paper
          </p>
        </div>
        
        {showResults ? (
          <div className="flex items-center gap-5">
            <div className="text-right">
              <p className={`text-4xl font-bold ${getScoreColor()}`}>
                {score}/{totalQuestions}
              </p>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1 font-medium">
                {Math.round((score / totalQuestions) * 100)}% • {getScoreMessage()}
              </p>
            </div>
            <button onClick={handleReset} className="btn-secondary">
              <RotateCcw className="w-5 h-5" />
              Retry Quiz
            </button>
          </div>
        ) : (
          <div className="text-right">
            <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-2 font-medium">
              Progress: {answeredCount} / {totalQuestions}
            </p>
            <div className="w-40 h-3 bg-neutral-200 dark:bg-neutral-700 rounded-full overflow-hidden shadow-inner-soft">
              <div 
                className="h-full bg-gradient-to-r from-primary-500 to-brand-500 transition-all duration-300 rounded-full"
                style={{ width: `${(answeredCount / totalQuestions) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      <div className="space-y-5">
        {quiz?.questions?.map((question, idx) => (
          <QuizQuestion
            key={question.id || idx}
            question={question}
            index={idx}
            onAnswer={handleAnswer}
            userAnswer={userAnswers[idx]}
            showResult={showResults}
          />
        ))}
      </div>

      {!showResults && (
        <div className="flex justify-center pt-6">
          <button
            onClick={handleSubmit}
            disabled={!canSubmit}
            className={`btn-gradient text-lg px-12 py-4 ${!canSubmit && 'opacity-50 cursor-not-allowed hover:scale-100'}`}
          >
            {canSubmit ? 'Submit Quiz' : `Answer all questions (${answeredCount}/${totalQuestions})`}
          </button>
        </div>
      )}
    </div>
  )
}
