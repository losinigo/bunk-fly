import { useChapters } from '../hooks/useQuestions'
import './ChapterSelect.css'

export default function ChapterSelect({ onSelect }) {
  const { chapters, loading } = useChapters()

  if (loading) {
    return <div className="loading">Loading chapters...</div>
  }

  const grouped = chapters.reduce((acc, ch) => {
    const lib = ch.libraries?.name || 'Unknown'
    if (!acc[lib]) acc[lib] = []
    acc[lib].push(ch)
    return acc
  }, {})

  return (
    <div className="chapter-select">
      <div className="app-header">
        <h1 className="app-title">✈️ BunkFly</h1>
        <p className="app-subtitle">FAA Test Prep</p>
      </div>

      {Object.entries(grouped).map(([library, chs]) => (
        <div key={library} className="library-group">
          <h2 className="library-name">{library}</h2>
          <div className="chapter-list">
            {chs.map(ch => (
              <button
                key={ch.id}
                className="chapter-btn"
                onClick={() => onSelect(ch)}
              >
                <span className="chapter-number">Ch. {ch.chapter_number}</span>
                <span className="chapter-section">{ch.section}</span>
                <span className="chapter-arrow">→</span>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
