import { ArrowLeftOutlined } from '@ant-design/icons'
import { Button, Progress, Typography, theme } from 'antd'
import { memo } from 'react'

import { AnalyzeOverlay } from './AnalyzeOverlay'
import { useAnalysisProgress, type AnalysisProgressStatus } from './useAnalysisProgress'

type AnalyzePhaseProps = {
  previewUrl: string
  status: AnalysisProgressStatus
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
    <div className="detection-stage">
      <img className="detection-image" src={previewUrl} alt="Meal being analyzed" />
      {showOverlay ? <AnalyzeOverlay /> : null}
    </div>
  )
})

export function AnalyzePhase({
  previewUrl,
  status,
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
              We couldn&apos;t analyze this photo.
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
              Analyzing your food…
            </Typography.Title>
            <Typography.Paragraph className="detection-subtitle">
              Detecting dishes and preparing nutrition information
            </Typography.Paragraph>
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
