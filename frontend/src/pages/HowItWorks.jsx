export default function HowItWorks() {
  const steps = ['User Input', 'Text Preprocessing', 'TF-IDF / NLP', 'Machine Learning', 'Prediction', 'Explainable AI', 'Web Verification', 'Final Assessment']
  return (
    <div className="container page">
      <h1>How It Works</h1>
      <div className="card">
        {steps.map((s, i) => (
          <div key={s}>
            <div className="pipeline-step">{s}</div>
            {i < steps.length - 1 && <div className="pipeline-arrow">↓</div>}
          </div>
        ))}
      </div>
      <div className="card">
        <h3>Important limitation</h3>
        <p>
          The ML model learns patterns from its training data. It does not possess human-like
          understanding of truth. Web verification provides additional evidence but is also not
          absolute proof. This is a decision-support tool.
        </p>
      </div>
    </div>
  )
}
