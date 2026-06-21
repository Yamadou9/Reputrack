import './App.css'
import { useState } from 'react'

function App() {
  const [recherche, setRecherche] = useState("")
  const [analyse, setAnalyse] = useState(null)
  const [chargement, setChargement] = useState(false)
  const [tri, setTri] = useState("pertinence")

  const postsTries = analyse?.posts
    ? [...analyse.posts].sort((a, b) =>
        tri === "score" ? b.score - a.score : b.pertinence - a.pertinence
      )
    : []

  const handleSearch = async () => {
    if (chargement) return
    const requete = recherche.trim()
    if (!requete) return
    setRecherche("")
    setChargement(true)
    try {
      const response = await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ marque: requete })
      })
      const data = await response.json()
      setAnalyse(data)
    } catch (e) {
      console.error("Erreur lors de l'analyse :", e)
    } finally {
      setChargement(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSearch()
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <span className="logo-icon">✦</span>
          <span className="logo-text">RepuTrack</span>
        </div>
        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Entrez un nom de marque (ex: Nike, Apple, Lidl...)"
            value={recherche}
            onChange={(e) => setRecherche(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={chargement}
          />
        </div>
        <button className="btn-search" onClick={handleSearch} disabled={chargement}>
          Analyser <span className="btn-arrow">→</span>
        </button>
      </header>

      <main className="content">
        {chargement ? (
          <p className="subtitle">Analyse en cours...</p>
        ) : !analyse ? (
          <>
            <div className="hero-icon">✦</div>
            <h1>Analysez la réputation d'une marque.</h1>
            <p className="subtitle">...</p>
          </>
        ) : (
          <div className="results">
            <section className="posts">
              <div className="posts-bar">
                <h2 className="posts-title">
                  Posts Reddit ({postsTries.length})
                </h2>
                <div className="sort-control">
                  <label htmlFor="tri">Trier par</label>
                  <select
                    id="tri"
                    value={tri}
                    onChange={(e) => setTri(e.target.value)}
                  >
                    <option value="pertinence">Pertinence</option>
                    <option value="score">Score</option>
                  </select>
                </div>
              </div>

              {postsTries.length === 0 ? (
                <p className="subtitle">Aucun post pertinent trouvé pour cette marque.</p>
              ) : (
                <div className="posts-grid">
                  {postsTries.map((post, i) => (
                    <a
                      key={i}
                      href={post.lien}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="post-card"
                    >
                      <div className="post-card-header">
                        <h4 className="post-card-title">{post.title}</h4>
                        <span className={`post-score sentiment-${post.sentiment}`}>
                          {post.score}
                        </span>
                      </div>

                      <p className="post-card-content">{post.content}</p>

                      <div className="post-card-footer">
                        <span className={`sentiment-tag sentiment-${post.sentiment}`}>
                          {post.sentiment}
                        </span>
                        <span className="pertinence-tag">
                          Pertinence {post.pertinence}%
                        </span>
                      </div>
                    </a>
                  ))}
                </div>
              )}
            </section>

            <aside className="summary">
              <div className="analyse-header">
                <div className={`score-badge sentiment-${analyse.sentiment_global}`}>
                  <span className="score-value">{analyse.score}</span>
                  <span className="score-max">/100</span>
                </div>
                <div className="sentiment-label">{analyse.sentiment_global}</div>
              </div>

              <p className="resume">{analyse.resume}</p>

              <div className="points">
                <div className="points-col positifs">
                  <h3>👍 Points positifs</h3>
                  <ul>
                    {analyse.points_positifs.map((point, i) => (
                      <li key={i}>{point}</li>
                    ))}
                  </ul>
                </div>
                <div className="points-col negatifs">
                  <h3>👎 Points négatifs</h3>
                  <ul>
                    {analyse.points_negatifs.map((point, i) => (
                      <li key={i}>{point}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="themes">
                {analyse.themes.map((theme, i) => (
                  <span key={i} className="theme-tag">{theme}</span>
                ))}
              </div>
            </aside>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
