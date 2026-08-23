import { ArrowLeftOutlined } from '@ant-design/icons'
import { Button, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'

import type { FoodPredictResponse } from '../../types/detection'

type ResultsPhaseProps = {
  previewUrl: string
  payload: FoodPredictResponse
  onRetake: () => void
}

export function ResultsPhase({ previewUrl, payload, onRetake }: ResultsPhaseProps) {
  const navigate = useNavigate()
  const receivedResponse = payload !== undefined && payload !== null

  return (
    <div className="detection-page">
      <div className="detection-top">
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          className="detection-back"
          aria-label="Back to dashboard"
          onClick={() => navigate('/dashboard')}
        />
      </div>
      <div className="detection-stage">
        <img className="detection-image" src={previewUrl} alt="Analyzed meal" />
      </div>
      <div className="detection-footer">
        <Typography.Title level={4} style={{ marginBottom: 4 }}>
          Results
        </Typography.Title>
        <Typography.Paragraph className="detection-subtitle">
          {receivedResponse
            ? 'Analysis complete. Detected dishes and nutrition will appear here when the prediction API includes them.'
            : 'Analysis complete.'}
        </Typography.Paragraph>
        <div className="detection-actions">
          <Button color="green" variant="solid" size="large" block onClick={onRetake}>
            Take another photo
          </Button>
        </div>
      </div>
    </div>
  )
}
