import { useState, useEffect } from 'react'
import { supabase } from '../lib/supabase'

export function useQuestions(chapterId) {
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchQuestions() {
      setLoading(true)
      setError(null)

      let query = supabase
        .from('questions')
        .select(`
          id,
          question_id,
          question,
          correct_answer,
          figure_id,
          figures (figure_ref, image_url),
          answers (letter, answer),
          explanations (letter, explanation)
        `)

      if (chapterId) {
        query = query.eq('chapter_id', chapterId)
      }

      const { data, error: fetchError } = await query

      if (fetchError) {
        setError(fetchError.message)
      } else {
        setQuestions(data || [])
      }
      setLoading(false)
    }

    fetchQuestions()
  }, [chapterId])

  return { questions, loading, error }
}

export function useChapters() {
  const [chapters, setChapters] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchChapters() {
      const { data } = await supabase
        .from('chapters')
        .select('id, chapter_number, section, library_id, libraries (name)')
        .order('chapter_number')

      setChapters(data || [])
      setLoading(false)
    }

    fetchChapters()
  }, [])

  return { chapters, loading }
}
