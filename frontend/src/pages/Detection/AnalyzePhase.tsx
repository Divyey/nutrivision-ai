import { ArrowLeftOutlined } from '@ant-design/icons'
import { Button, Progress, Typography, theme } from 'antd'
import { memo } from 'react'

import { AnalyzeOverlay } from './AnalyzeOverlay'
import { useAnalysisProgress, type AnalysisProgressStatus } from './useAnalysisProgress'

type AnalyzePhaseProps = {
  previewUrl: string
  status: AnalysisProgressStatus
  errorMessage?: string
  onCancel: () => void
  onTryAgain?: () => void
  onChooseAnother?: () => void
}

const AnalysisImage = memo(function AnalysisImage({
  previewUrl,
  showOverlay,
}: {
  previewUrl: string
  showOverlay: boolean
}) {
  return (
    <div className="detection-stage detection-stage-results">
      <div className="detection-results-frame">
        <img className="detection-image-contain" src={previewUrl} alt="Meal being analyzed" />
        {showOverlay ? <AnalyzeOverlay /> : null}
      </div>
    </div>
  )
})

function runningCopy(percent: number, status: AnalysisProgressStatus) {
  if (status === 'success') {
    return {
      title: 'Dishes found',
      subtitle: 'Opening results…',
    }
  }
  if (percent < 35) {
    return {
      title: 'Scanning photo…',
      subtitle: 'Looking for dishes in the frame',
    }
  }
  if (percent < 72) {
    return {
      title: 'Identifying dishes…',
      subtitle: 'Matching items in your photo',
    }
  }
  return {
    title: 'Almost done…',
    subtitle: 'Preparing your results',
  }
}

export function AnalyzePhase({
  previewUrl,
  status,
  errorMessage,
  onCancel,
  onTryAgain,
  onChooseAnother,
}: AnalyzePhaseProps) {
  const percent = useAnalysisProgress(status)
  const {
    token: { colorSuccess },
  } = theme.useToken()
  const isError = status === 'error'
  const progressStatus = isError ? 'exception' : status === 'success' ? 'success' : 'active'
  const copy = runningCopy(percent, status)

  return (
    <div className="detection-page">
      <div className="detection-top">
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          className="detection-back"
          aria-label="Cancel analysis"
          onClick={onCancel}
        />
      </div>
      <AnalysisImage previewUrl={previewUrl} showOverlay={status === 'running'} />
      <div className="detection-footer">
        {isError ? (
          <>
            <Typography.Title level={4} style={{ marginBottom: 4 }}>
              {errorMessage ?? "We couldn't analyze this photo."}
            </Typography.Title>
            <Typography.Paragraph className="detection-subtitle">
              Please try again or choose another photo.
            </Typography.Paragraph>
            <div className="detection-actions">
              <Button color="green" variant="solid" size="large" block onClick={onTryAgain}>
                Try Again
              </Button>
              <Button size="large" block onClick={onChooseAnother}>
                Choose Another Photo
              </Button>
            </div>
          </>
        ) : (
          <>
            <Typography.Title level={4} style={{ marginBottom: 4 }} aria-live="polite">
              {copy.title}
            </Typography.Title>
            <Typography.Paragraph className="detection-subtitle">{copy.subtitle}</Typography.Paragraph>
            <Progress
              className="detection-progress"
              percent={percent}
              status={progressStatus}
              strokeColor={colorSuccess}
              trailColor="rgba(255, 255, 255, 0.16)"
              aria-label="Analysis progress"
            />
          </>
        )}
      </div>
    </div>
  )
}
