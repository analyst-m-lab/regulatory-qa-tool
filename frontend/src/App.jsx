import { useState, useEffect } from 'react'
import './App.css'

export default function App() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [online, setOnline] = useState(null)

  useEffect(() => {
    fetch('/api/status')
      .then(r => r.json())
      .then(d => setOnline(d.rag_initialized))
      .catch(() => setOnline(false))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!question.trim()) return

    setLoading(true)
    setResult(null)
    setError(null)

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.trim() }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Request failed')
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Regulatory Q&amp;A Tool</h1>
        <span className={`header-badge${online === false ? ' offline' : ''}`}>
          {online === null ? 'Connecting...' : online ? 'RAG Ready' : 'Offline'}
        </span>
      </header>

      <main className="main">
        <section className="query-box">
          <label htmlFor="question">Ask a regulatory question</label>
          <form className="input-row" onSubmit={handleSubmit}>
            <input
              id="question"
              className="query-input"
              type="text"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="e.g. What are ICH Q1A stability testing requirements?"
              disabled={loading}
              autoFocus
            />
            <button className="submit-btn" type="submit" disabled={loading || !question.trim()}>
              {loading ? 'Searching...' : 'Ask'}
            </button>
          </form>
        </section>

        {loading && (
          <div className="answer-box">
            <div className="loading">
              <div className="spinner" />
              Searching knowledge base...
            </div>
          </div>
        )}

        {error && (
          <div className="answer-box">
            <h2>Error</h2>
            <p className="answer-error">{error}</p>
          </div>
        )}

        {result && !loading && (
          <>
            <section className="answer-box">
              <h2>Answer</h2>
              <p className="answer-text">{result.answer}</p>
            </section>

            {result.sources && result.sources.length > 0 && (
              <section className="sources-box">
                <h2>Sources ({result.sources.length})</h2>
                <div className="source-list">
                  {result.sources.map((src, i) => (
                    <div className="source-item" key={i}>
                      <span className="source-icon">📄</span>
                      <span className="source-name">{src.filename || src.source}</span>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}

        {!loading && !result && !error && (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p>Enter a question above to search regulatory guidelines</p>
          </div>
        )}
      </main>
    </div>
  )
}
