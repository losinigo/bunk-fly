import { useState } from 'react'
import './QuestionCard.css'

export default function QuestionCard({ question, index, total, onAnswer }) {
  const [selected, setSelected] = useState(null)
  const [showResult, setShowResult] = useState(false)

  const isCorrect = selected === question.correct_answer

  function handleSelect(letter) {
    if (showResult) return
    setSelected(letter)
  }

  function handleSubmit() {
    if (!selected) return
    setShowResult(true)
    onAnswer(isCorrect)
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

  const sortedAnswers = [...(question.answers || [])].sort((a, b) =>
    a.letter.localeCompare(b.letter)
  )

  return (
    <div className="question-card">
      <div className="question-header">
        <span className="question-number">Question {index + 1} of {total}</span>
        <span className="question-id">{question.question_id}</span>
      </div>

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
