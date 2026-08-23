export function AnalyzeOverlay() {
  return (
    <div className="analyze-overlay" aria-hidden="true">
      <div className="analyze-vignette" />
      <div className="analyze-viewfinder">
        <span className="analyze-corner analyze-corner-tl" />
        <span className="analyze-corner analyze-corner-tr" />
        <span className="analyze-corner analyze-corner-bl" />
        <span className="analyze-corner analyze-corner-br" />
      </div>
      <span className="analyze-scan-line" />
    </div>
  )
}
