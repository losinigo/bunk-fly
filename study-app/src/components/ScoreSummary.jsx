import './ScoreSummary.css'

export default function ScoreSummary({ score, total, chapter, onRestart, onBack }) {
  const percentage = Math.round((score / total) * 100)
  const passed = percentage >= 70

  return (
    <div className="score-summary">
      <div className={`score-circle ${passed ? 'pass' : 'fail'}`}>
        <span className="score-percent">{percentage}%</span>
        <span className="score-label">{score}/{total}</span>
      </div>

      <h2 className="score-title">
        {passed ? 'Great job!' : 'Keep studying!'}
      </h2>

      <p className="score-subtitle">
        {chapter?.section || 'Study Session'}
      </p>

      <p className="score-message">
        {passed
          ? 'You passed! You\'re on the right track.'
          : 'You need 70% to pass. Review the material and try again.'}
      </p>

      <div className="score-actions">
        <button className="restart-btn" onClick={onRestart}>Try Again</button>
        <button className="back-to-menu-btn" onClick={onBack}>Back to Menu</button>
      </div>
    </div>
  )
}
