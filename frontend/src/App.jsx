import './App.css'
import { useState } from 'react'

function App() {
  const [recherche, setRecherche] = useState("")
  const [resultats, setResultats] = useState([])

   const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      console.log("Recherche :", recherche) // fais ton action ici
      setRecherche("") // remet l'input à vide
    }
  }

  const handleSearch = async () => {
    const response = await fetch("http://localhost:8000/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ marque: recherche })
    }
    )
    const data = await response.json()
    console.log(data.queries)
    setRecherche("")
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
          />
        </div>
        <button className="btn-search" onClick={handleSearch}>Analyser</button>
      </header>

    <main className="content">
      {resultats.length === 0 ? (
      <>
        <div className="hero-icon">✦</div>
        <h1>Analysez la réputation d'une marque.</h1>
        <p className="subtitle">...</p>
      </>
    ) : (
      <ul className="results">
        {resultats.map((post) => (
          <li key={post.id} className="result-card">
            <h3>{post.titre}</h3>
            <p>{post.extrait}</p>
            <span>{post.score}</span>
          </li>
        ))}
      </ul>
    )}
    </main>
    </div>
  )
}

export default App
