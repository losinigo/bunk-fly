import { useState } from 'react'
import './QuestionCard.css'

export default function QuestionCard({ question, index, total, answers, onAnswer, onNavigate }) {
  const alreadyAnswered = index in answers
  const [selected, setSelected] = useState(null)
  const [showResult, setShowResult] = useState(alreadyAnswered)
  const [showNav, setShowNav] = useState(false)

  const isCorrect = alreadyAnswered
    ? answers[index] === 'correct'
    : selected === question.correct_answer

  function handleSelect(letter) {
    if (showResult) return
    setSelected(letter)
  }

  function handleSubmit() {
    if (!selected) return
    setShowResult(true)
    onAnswer(selected === question.correct_answer)
  }

  function getExplanation(letter) {
    return question.explanations?.find(e => e.letter === letter)?.explanation
  }

  function getAnswerClass(letter) {
    if (!showResult) return selected === letter ? 'selected' : ''
    if (letter === question.correct_answer) return 'correct'
    if (letter === selected && !isCorrect) return 'incorrect'
    return ''
  }

  function getNavItemClass(i) {
    if (!(i in answers)) return 'nav-item'
    return `nav-item ${answers[i]}`
  }

  const sortedAnswers = [...(question.answers || [])].sort((a, b) =>
    a.letter.localeCompare(b.letter)
  )

  return (
    <div className="question-card">
      <div className="question-header">
        <div className="question-header-left">
          <button className="grid-nav-btn" onClick={() => setShowNav(v => !v)} aria-label="Question navigation">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <rect x="1" y="1" width="4.5" height="4.5" rx="1" fill="currentColor"/>
              <rect x="6.75" y="1" width="4.5" height="4.5" rx="1" fill="currentColor"/>
              <rect x="12.5" y="1" width="4.5" height="4.5" rx="1" fill="currentColor"/>
              <rect x="1" y="6.75" width="4.5" height="4.5" rx="1" fill="currentColor"/>
              <rect x="6.75" y="6.75" width="4.5" height="4.5" rx="1" fill="currentColor"/>
              <rect x="12.5" y="6.75" width="4.5" height="4.5" rx="1" fill="currentColor"/>
              <rect x="1" y="12.5" width="4.5" height="4.5" rx="1" fill="currentColor"/>
              <rect x="6.75" y="12.5" width="4.5" height="4.5" rx="1" fill="currentColor"/>
              <rect x="12.5" y="12.5" width="4.5" height="4.5" rx="1" fill="currentColor"/>
            </svg>
          </button>
          <span className="question-number">Question {index + 1} of {total}</span>
        </div>
        <span className="question-id">{question.question_id}</span>
      </div>

      {showNav && (
        <div className="nav-overlay" onClick={() => setShowNav(false)}>
          <div className="nav-grid" onClick={e => e.stopPropagation()}>
            {Array.from({ length: total }, (_, i) => (
              <button
                key={i}
                className={`${getNavItemClass(i)}${i === index ? ' current' : ''}`}
                onClick={() => { onNavigate(i); setShowNav(false) }}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </div>
      )}

      {question.figures?.image_url && (
        <div className="question-figure">
          <img src={question.figures.image_url} alt={question.figures.figure_ref} />
          <span className="figure-ref">{question.figures.figure_ref}</span>
        </div>
      )}

      <p className="question-text">{question.question}</p>

      <div className="answers">
        {sortedAnswers.map(({ letter, answer }) => (
          <button
            key={letter}
            className={`answer-btn ${getAnswerClass(letter)}`}
            onClick={() => handleSelect(letter)}
          >
            <span className="answer-letter">{letter}</span>
            <span className="answer-text">{answer}</span>
          </button>
        ))}
      </div>

      {showResult && (
        <div className={`explanation ${isCorrect ? 'correct' : 'incorrect'}`}>
          <p className="result-label">{isCorrect ? '✓ Correct!' : '✗ Incorrect'}</p>
          <p className="explanation-text">
            {getExplanation(question.correct_answer)}
          </p>
        </div>
      )}

      {!showResult && (
        <button
          className="submit-btn"
          onClick={handleSubmit}
          disabled={!selected}
        >
          Submit Answer
        </button>
      )}
    </div>
  )
}
