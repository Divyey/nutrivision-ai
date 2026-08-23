import { ArrowLeftOutlined } from '@ant-design/icons'
import { Button, Typography } from 'antd'

type ReviewPhaseProps = {
  previewUrl: string
  onUsePhoto: () => void
  onRetake: () => void
}

export function ReviewPhase({ previewUrl, onUsePhoto, onRetake }: ReviewPhaseProps) {
  return (
    <div className="detection-page">
      <div className="detection-top">
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          className="detection-back"
          aria-label="Retake photo"
          onClick={onRetake}
        />
      </div>
      <div className="detection-stage">
        <img className="detection-image" src={previewUrl} alt="Captured meal" />
      </div>
      <div className="detection-footer">
        <Typography.Title level={4} style={{ marginBottom: 4 }}>
          Use this photo?
        </Typography.Title>
        <Typography.Paragraph className="detection-subtitle">
          We will analyze the dishes in this picture.
        </Typography.Paragraph>
        <div className="detection-actions">
          <Button color="green" variant="solid" size="large" block onClick={onUsePhoto}>
            Use photo
          </Button>
          <Button size="large" block onClick={onRetake}>
            Retake
          </Button>
        </div>
      </div>
    </div>
  )
}
