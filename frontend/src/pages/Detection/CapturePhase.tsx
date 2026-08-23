import { ArrowLeftOutlined } from '@ant-design/icons'
import { App, Button, Typography } from 'antd'
import { useRef, type ChangeEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  ALLOWED_IMAGE_ACCEPT,
  isAllowedImageFile,
  UNSUPPORTED_IMAGE_MESSAGE,
} from '../../types/detection'

type CapturePhaseProps = {
  onPhotoSelected: (file: File) => void
}

export function CapturePhase({ onPhotoSelected }: CapturePhaseProps) {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const galleryInputRef = useRef<HTMLInputElement>(null)

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) {
      return
    }
    if (!isAllowedImageFile(file)) {
      message.error(UNSUPPORTED_IMAGE_MESSAGE)
      return
    }
    onPhotoSelected(file)
  }

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
      <div className="detection-stage detection-stage-empty">
        <Typography.Title level={4} style={{ color: '#fff', margin: 0 }}>
          Add a photo of your meal
        </Typography.Title>
        <Typography.Paragraph className="detection-subtitle">
          Take a picture or choose one from your gallery to analyze.
        </Typography.Paragraph>
      </div>
      <div className="detection-footer">
        <div className="detection-actions">
          <input
            ref={cameraInputRef}
            type="file"
            accept={ALLOWED_IMAGE_ACCEPT}
            capture="environment"
            hidden
            onChange={handleFileChange}
          />
          <input
            ref={galleryInputRef}
            type="file"
            accept={ALLOWED_IMAGE_ACCEPT}
            hidden
            onChange={handleFileChange}
          />
          <Button
            color="green"
            variant="solid"
            size="large"
            block
            onClick={() => cameraInputRef.current?.click()}
          >
            Take photo
          </Button>
          <Button size="large" block onClick={() => galleryInputRef.current?.click()}>
            Choose from gallery
          </Button>
        </div>
      </div>
    </div>
  )
}
