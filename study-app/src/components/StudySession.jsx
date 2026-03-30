import { useState } from 'react'
import QuestionCard from './QuestionCard'
import ScoreSummary from './ScoreSummary'
import './StudySession.css'

export default function StudySession({ questions, chapter, onBack }) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [finished, setFinished] = useState(false)

  const score = Object.values(answers).filter(a => a === 'correct').length
  const answered = Object.keys(answers).length

  function handleAnswer(isCorrect) {
    setAnswers(prev => ({ ...prev, [currentIndex]: isCorrect ? 'correct' : 'incorrect' }))
  }

  function handleNext() {
    if (currentIndex + 1 >= questions.length) {
      setFinished(true)
    } else {
      setCurrentIndex(i => i + 1)
    }
  }

  function handleRestart() {
    setCurrentIndex(0)
    setAnswers({})
    setFinished(false)
  }

  if (finished) {
    return (
      <ScoreSummary
        score={score}
        total={questions.length}
        chapter={chapter}
        onRestart={handleRestart}
        onBack={onBack}
      />
    )
  }

  const current = questions[currentIndex]
  const hasAnswered = currentIndex in answers

  return (
    <div className="study-session">
      <div className="session-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
        <div className="progress-info">
          <span>{score}/{answered} correct</span>
        </div>
      </div>

      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
        />
      </div>

      <QuestionCard
        key={`${current.id}-${currentIndex}`}
        question={current}
        index={currentIndex}
        total={questions.length}
        answers={answers}
        onAnswer={handleAnswer}
        onNavigate={setCurrentIndex}
      />

      {hasAnswered && (
        <button className="next-btn" onClick={handleNext}>
          {currentIndex + 1 >= questions.length ? 'See Results' : 'Next Question →'}
        </button>
      )}
    </div>
  )
}
