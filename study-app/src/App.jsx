import { useState } from 'react'
import ChapterSelect from './components/ChapterSelect'
import StudySession from './components/StudySession'
import { useQuestions } from './hooks/useQuestions'
import './App.css'

function App() {
  const [selectedChapter, setSelectedChapter] = useState(null)
  const { questions, loading, error } = useQuestions(selectedChapter?.id)

  if (!selectedChapter) {
    return <ChapterSelect onSelect={setSelectedChapter} />
  }

  if (loading) {
    return <div className="loading-screen">Loading questions...</div>
  }

  if (error) {
    return (
      <div className="error-screen">
        <p>Failed to load questions</p>
        <button onClick={() => setSelectedChapter(null)}>Go Back</button>
      </div>
    )
  }

  return (
    <StudySession
      questions={questions}
      chapter={selectedChapter}
      onBack={() => setSelectedChapter(null)}
    />
  )
}

export default App
