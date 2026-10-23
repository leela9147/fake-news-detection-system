import { Link } from 'react-router-dom'

export default function Landing() {
  return (
    <div>
      <section className="hero">
        <div className="container hero-inner">
          <h1>Fake News Detection & Verification</h1>
          <p>Analyze news using machine learning and compare the result with current real-world evidence.</p>
          <div className="hero-actions">
            <Link to="/signup" className="btn btn-primary btn-lg">Get Started</Link>
            <Link to="/login" className="btn btn-outline btn-lg">Login</Link>
          </div>
        </div>
      </section>

      <section className="section container">
        <h2>How It Works</h2>
        <div className="grid-3">
          {[
            ['1. Submit', 'Paste the headline and full article you want to check.'],
            ['2. Analyze', 'Our ML model classifies the article and explains its reasoning.'],
            ['3. Verify', 'We compare the claim against current sources from the web.'],
          ].map(([t, d]) => <div key={t} className="card"><h3>{t}</h3><p>{d}</p></div>)}
        </div>
      </section>

      <section className="section alt">
        <div className="container grid-4">
          {[
            ['Machine Learning', 'Logistic Regression, Linear SVM and Random Forest compared on real data.'],
            ['Explainable AI', 'Every prediction comes with human-readable and technical explanations.'],
            ['Real-World Verification', 'Searches current sources and shows supporting or contradicting evidence.'],
            ['Why Verification Matters', 'ML patterns are not proof. External evidence gives essential context.'],
          ].map(([t, d]) => <div key={t} className="card"><h3>{t}</h3><p>{d}</p></div>)}
        </div>
      </section>

      <section className="section container">
        <h2>Features</h2>
        <div className="grid-3">
          {['Account system with secure password hashing', 'Prediction history with search & filters',
            'Model insights dashboard with real metrics', 'Supporting & contradicting source cards',
            'Needs Verification state instead of forced answers', 'Responsive UI with dark mode',
          ].map(f => <div key={f} className="card"><p>✔ {f}</p></div>)}
        </div>
      </section>

      <section className="section alt">
        <div className="container">
          <h2>About Project</h2>
          <p>
            The ML model learns patterns from its training data. It does not possess human-like
            understanding of truth. Web verification provides additional evidence but is also not
            absolute proof. This system is a decision-support tool that helps users investigate
            questionable news — it does not claim perfect factual certainty.
          </p>
        </div>
      </section>
    </div>
  )
}
