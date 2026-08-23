import { useEffect, useState } from 'react'

export type AnalysisProgressStatus = 'running' | 'success' | 'error'

export function useAnalysisProgress(status: AnalysisProgressStatus): number {
  const [percent, setPercent] = useState(10)

  useEffect(() => {
    if (status !== 'running') {
      return
    }

    const startedAt = performance.now()
    let frame = 0

    const tick = (now: number) => {
      const elapsed = now - startedAt
      let next: number
      if (elapsed < 1400) {
        const t = Math.min(1, elapsed / 1400)
        const eased = 1 - (1 - t) ** 3
        next = 10 + eased * 58
      } else {
        const t2 = 1 - Math.exp(-(elapsed - 1400) / 3500)
        const base = 68 + t2 * 20
        const wave = Math.sin(elapsed / 1100) * 2.5
        next = Math.min(90, Math.max(70, base + wave))
      }
      setPercent(Math.round(next))
      frame = requestAnimationFrame(tick)
    }

    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [status])

  if (status === 'success') {
    return 100
  }
  return percent
}
