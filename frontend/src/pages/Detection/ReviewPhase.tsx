import {
  ArrowLeftOutlined,
  ArrowRightOutlined,
  CameraOutlined,
  CheckCircleFilled,
  CoffeeOutlined,
  LockOutlined,
  ScanOutlined,
  StarFilled,
  SunOutlined,
} from '@ant-design/icons'
import { Button, Typography } from 'antd'
import type { ReactNode } from 'react'

type ReviewPhaseProps = {
  previewUrl: string
  onUsePhoto: () => void
  onRetake: () => void
}

const TIPS: { icon: ReactNode; title: string; copy: string }[] = [
  { icon: <SunOutlined />, title: 'Good lighting', copy: 'Bright, natural light works best.' },
  { icon: <ScanOutlined />, title: 'Top view', copy: 'Try to capture from above.' },
  { icon: <CoffeeOutlined />, title: 'Single dish', copy: 'Keep one main dish in the frame.' },
]

export function ReviewPhase({ previewUrl, onUsePhoto, onRetake }: ReviewPhaseProps) {
  return (
    <div className="detection-page detection-page-review">
      <div className="detection-top">
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          className="detection-back"
          aria-label="Retake photo"
          onClick={onRetake}
        />
      </div>
      <div className="detection-review-heading">
        <CheckCircleFilled className="detection-review-check" aria-hidden />
        <Typography.Title level={4} className="detection-review-title">
          Photo captured!
        </Typography.Title>
        <Typography.Paragraph className="detection-subtitle">
          Review your photo before we analyze your food.
        </Typography.Paragraph>
      </div>
      <div className="detection-stage detection-stage-review">
        <img className="detection-image" src={previewUrl} alt="Captured meal" />
      </div>
      <div className="detection-footer">
        <div className="detection-tips">
          <p className="detection-tips-title">Tips for best results</p>
          {TIPS.map((tip) => (
            <div key={tip.title} className="detection-tip">
              <span className="detection-tip-icon">{tip.icon}</span>
              <strong className="detection-tip-name">{tip.title}</strong>
              <span className="detection-tip-copy">{tip.copy}</span>
            </div>
          ))}
        </div>
        <div className="detection-actions">
          <Button color="green" variant="solid" size="large" block onClick={onUsePhoto}>
            <StarFilled />
            Analyze this photo
            <ArrowRightOutlined />
          </Button>
          <Button size="large" block icon={<CameraOutlined />} onClick={onRetake}>
            Retake photo
          </Button>
        </div>
        <p className="detection-privacy">
          <LockOutlined /> Your photo is private and secure
        </p>
      </div>
    </div>
  )
}
