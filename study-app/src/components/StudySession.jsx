import { useState } from 'react'
import QuestionCard from './QuestionCard'
import ScoreSummary from './ScoreSummary'
import './StudySession.css'

export default function StudySession({ questions, chapter, onBack }) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [score, setScore] = useState(0)
  const [answered, setAnswered] = useState(0)
  const [finished, setFinished] = useState(false)

  function handleAnswer(isCorrect) {
    if (isCorrect) setScore(s => s + 1)
    setAnswered(a => a + 1)
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
    setScore(0)
    setAnswered(0)
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
  const hasAnswered = answered > currentIndex

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
        key={current.id}
        question={current}
        index={currentIndex}
        total={questions.length}
        onAnswer={handleAnswer}
      />

      {hasAnswered && (
        <button className="next-btn" onClick={handleNext}>
          {currentIndex + 1 >= questions.length ? 'See Results' : 'Next Question →'}
        </button>
      )}
    </div>
  )
}
