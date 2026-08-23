import { useCallback, useEffect, useRef, useState } from 'react'

import { isAbortError, HttpError } from '../../lib/http'
import { DetectionService } from '../../services/DetectionService/DetectionService'
import type { DetectionPhase } from '../../types/detection'
import { AnalyzePhase } from './AnalyzePhase'
import { CapturePhase } from './CapturePhase'
import { ResultsPhase } from './ResultsPhase'
import { ReviewPhase } from './ReviewPhase'

const MIN_ANALYZE_MS = 500
const SUCCESS_HOLD_MS = 300

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

export function DetectionPage() {
  const [phase, setPhase] = useState<DetectionPhase>({ name: 'capture' })
  const [analysisRunId, setAnalysisRunId] = useState(0)
  const generationRef = useRef(0)
  const abortRef = useRef<AbortController | null>(null)
  const previewUrlRef = useRef<string | null>(null)

  const releasePreview = useCallback(() => {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current)
      previewUrlRef.current = null
    }
  }, [])

  useEffect(() => {
    return () => {
      generationRef.current += 1
      abortRef.current?.abort()
      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current)
      }
    }
  }, [])

  useEffect(() => {
    if (phase.name !== 'completing') {
      return
    }
    const generation = generationRef.current
    const next = {
      file: phase.file,
      previewUrl: phase.previewUrl,
      payload: phase.payload,
    }
    const timer = window.setTimeout(() => {
      if (generation !== generationRef.current) {
        return
      }
      setPhase({ name: 'results', ...next })
    }, SUCCESS_HOLD_MS)
    return () => window.clearTimeout(timer)
  }, [phase])

  function goToCapture() {
    generationRef.current += 1
    abortRef.current?.abort()
    releasePreview()
    setPhase({ name: 'capture' })
  }

  function previewFile(file: File): string {
    releasePreview()
    const previewUrl = URL.createObjectURL(file)
    previewUrlRef.current = previewUrl
    return previewUrl
  }

  function onCameraPhoto(file: File) {
    const previewUrl = previewFile(file)
    setPhase({ name: 'review', file, previewUrl })
  }

  function onLibraryPhoto(file: File) {
    const previewUrl = previewFile(file)
    startAnalysis(file, previewUrl)
  }

  function startAnalysis(file: File, previewUrl: string) {
    const generation = ++generationRef.current
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller
    setAnalysisRunId((id) => id + 1)
    setPhase({ name: 'analyzing', file, previewUrl })
    void runAnalysis(file, previewUrl, generation, controller.signal)
  }

  async function runAnalysis(
    file: File,
    previewUrl: string,
    generation: number,
    signal: AbortSignal,
  ) {
    const startedAt = Date.now()
    try {
      const payload = await DetectionService.analyze(file, signal)
      if (generation !== generationRef.current) {
        return
      }
      setPhase({ name: 'completing', file, previewUrl, payload })
    } catch (error) {
      if (signal.aborted || isAbortError(error) || generation !== generationRef.current) {
        return
      }
      const elapsed = Date.now() - startedAt
      if (elapsed < MIN_ANALYZE_MS) {
        await sleep(MIN_ANALYZE_MS - elapsed)
      }
      if (generation !== generationRef.current) {
        return
      }
      const message =
        error instanceof HttpError && error.status === 503
          ? "Food analysis isn't available right now."
          : "We couldn't analyze this photo."
      setPhase({
        name: 'error',
        file,
        previewUrl,
        message,
      })
    }
  }

  function cancelAnalysis() {
    if (phase.name !== 'analyzing' && phase.name !== 'completing' && phase.name !== 'error') {
      return
    }
    generationRef.current += 1
    abortRef.current?.abort()
    setPhase({ name: 'review', file: phase.file, previewUrl: phase.previewUrl })
  }

  if (phase.name === 'capture') {
    return (
      <CapturePhase onCameraPhoto={onCameraPhoto} onLibraryPhoto={onLibraryPhoto} />
    )
  }

  if (phase.name === 'review') {
    return (
      <ReviewPhase
        previewUrl={phase.previewUrl}
        onUsePhoto={() => startAnalysis(phase.file, phase.previewUrl)}
        onRetake={goToCapture}
      />
    )
  }

  if (phase.name === 'analyzing' || phase.name === 'completing' || phase.name === 'error') {
    const status =
      phase.name === 'error' ? 'error' : phase.name === 'completing' ? 'success' : 'running'
    return (
      <AnalyzePhase
        key={analysisRunId}
        previewUrl={phase.previewUrl}
        status={status}
        errorMessage={phase.name === 'error' ? phase.message : undefined}
        onCancel={cancelAnalysis}
        onTryAgain={
          phase.name === 'error' ? () => startAnalysis(phase.file, phase.previewUrl) : undefined
        }
        onChooseAnother={phase.name === 'error' ? goToCapture : undefined}
      />
    )
  }

  return (
    <ResultsPhase
      previewUrl={phase.previewUrl}
      payload={phase.payload}
      onRetake={goToCapture}
    />
  )
}
