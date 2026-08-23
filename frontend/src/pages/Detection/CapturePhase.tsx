import { ArrowLeftOutlined } from '@ant-design/icons'
import { App, Button, Typography } from 'antd'
import { useRef, useState, type ChangeEvent, type DragEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  ALLOWED_IMAGE_ACCEPT,
  isAllowedImageFile,
  UNSUPPORTED_IMAGE_MESSAGE,
} from '../../types/detection'

type CapturePhaseProps = {
  onCameraPhoto: (file: File) => void
  onLibraryPhoto: (file: File) => void
}

export function CapturePhase({ onCameraPhoto, onLibraryPhoto }: CapturePhaseProps) {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const galleryInputRef = useRef<HTMLInputElement>(null)
  const dragDepthRef = useRef(0)
  const [isDragging, setIsDragging] = useState(false)

  function takeFile(file: File | undefined, autoAnalyze: boolean) {
    if (!file) {
      return
    }
    if (!isAllowedImageFile(file)) {
      message.error(UNSUPPORTED_IMAGE_MESSAGE)
      return
    }
    if (autoAnalyze) {
      onLibraryPhoto(file)
      return
    }
    onCameraPhoto(file)
  }

  function handleCameraChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    takeFile(file, false)
  }

  function handleGalleryChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    takeFile(file, true)
  }

  function handleDragEnter(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    dragDepthRef.current += 1
    setIsDragging(true)
  }

  function handleDragOver(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'copy'
  }

  function handleDragLeave(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    dragDepthRef.current -= 1
    if (dragDepthRef.current <= 0) {
      dragDepthRef.current = 0
      setIsDragging(false)
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    dragDepthRef.current = 0
    setIsDragging(false)
    takeFile(event.dataTransfer.files[0], true)
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
      <div
        className={`detection-stage detection-stage-empty${isDragging ? ' detection-stage-drop' : ''}`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Typography.Title level={4} style={{ color: '#fff', margin: 0 }}>
          Add a photo of your meal
        </Typography.Title>
        <Typography.Paragraph className="detection-subtitle">
          Take a picture, choose one from your gallery, or drop a photo here.
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
            onChange={handleCameraChange}
          />
          <input
            ref={galleryInputRef}
            type="file"
            accept={ALLOWED_IMAGE_ACCEPT}
            hidden
            onChange={handleGalleryChange}
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
