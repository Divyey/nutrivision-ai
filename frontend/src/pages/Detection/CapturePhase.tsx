import { ArrowLeftOutlined, PictureOutlined, SyncOutlined } from '@ant-design/icons'
import { App, Button, Spin, Typography } from 'antd'
import { useEffect, useRef, useState, type ChangeEvent, type DragEvent } from 'react'
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

type CameraStatus = 'starting' | 'live' | 'unavailable'
type FacingMode = 'environment' | 'user'

function stopStream(stream: MediaStream | null) {
  stream?.getTracks().forEach((track) => track.stop())
}

async function requestCameraStream(facingMode: FacingMode): Promise<MediaStream> {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new Error('Camera is not supported')
  }
  try {
    return await navigator.mediaDevices.getUserMedia({
      audio: false,
      video: { facingMode: { exact: facingMode } },
    })
  } catch {
    try {
      return await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: { facingMode: { ideal: facingMode } },
      })
    } catch {
      return await navigator.mediaDevices.getUserMedia({ audio: false, video: true })
    }
  }
}

export function CapturePhase({ onCameraPhoto, onLibraryPhoto }: CapturePhaseProps) {
  const navigate = useNavigate()
  const { message } = App.useApp()
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const galleryInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const dragDepthRef = useRef(0)
  const [cameraStatus, setCameraStatus] = useState<CameraStatus>('starting')
  const [facingMode, setFacingMode] = useState<FacingMode>('environment')
  const [capturing, setCapturing] = useState(false)
  const [isDragging, setIsDragging] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function startCamera() {
      setCameraStatus((status) => (status === 'live' ? status : 'starting'))
      try {
        const stream = await requestCameraStream(facingMode)
        if (cancelled) {
          stopStream(stream)
          return
        }
        stopStream(streamRef.current)
        streamRef.current = stream
        const video = videoRef.current
        if (video) {
          video.srcObject = stream
          await video.play()
        }
        if (cancelled) {
          stopStream(stream)
          return
        }
        setCameraStatus('live')
      } catch {
        if (!cancelled) {
          setCameraStatus('unavailable')
        }
      }
    }

    void startCamera()

    return () => {
      cancelled = true
      stopStream(streamRef.current)
      streamRef.current = null
      const video = videoRef.current
      if (video) {
        video.srcObject = null
      }
    }
  }, [facingMode])

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

  function captureFrame() {
    const video = videoRef.current
    if (!video || video.videoWidth === 0 || !streamRef.current) {
      cameraInputRef.current?.click()
      return
    }
    if (capturing) {
      return
    }
    setCapturing(true)
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    const context = canvas.getContext('2d')
    if (!context) {
      setCapturing(false)
      cameraInputRef.current?.click()
      return
    }
    if (facingMode === 'user') {
      context.translate(canvas.width, 0)
      context.scale(-1, 1)
    }
    context.drawImage(video, 0, 0)
    canvas.toBlob(
      (blob) => {
        setCapturing(false)
        if (!blob) {
          message.error('Could not capture this frame.')
          return
        }
        takeFile(new File([blob], 'meal.jpg', { type: 'image/jpeg' }), false)
      },
      'image/jpeg',
      0.92,
    )
  }

  return (
    <div
      className={`detection-page detection-page-camera${isDragging ? ' detection-stage-drop' : ''}`}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="detection-stage detection-stage-camera">
        <video
          ref={videoRef}
          className={
            facingMode === 'user'
              ? 'detection-camera-video detection-camera-video-selfie'
              : 'detection-camera-video'
          }
          autoPlay
          muted
          playsInline
          aria-label="Camera preview"
        />
        {cameraStatus !== 'live' ? (
          <div className="detection-camera-status">
            {cameraStatus === 'starting' ? (
              <Spin />
            ) : (
              <Typography.Paragraph className="detection-subtitle">
                Camera isn’t available. Choose a photo from your gallery.
              </Typography.Paragraph>
            )}
          </div>
        ) : null}
      </div>
      <div className="detection-camera-top">
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          className="detection-back"
          aria-label="Back to dashboard"
          onClick={() => navigate('/dashboard')}
        />
      </div>
      <div className="detection-camera-bar">
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
          type="text"
          className="detection-gallery"
          aria-label="Choose from gallery"
          icon={<PictureOutlined />}
          onClick={() => galleryInputRef.current?.click()}
        />
        <Button
          type="text"
          className="detection-shutter"
          aria-label="Take photo"
          disabled={capturing}
          onClick={captureFrame}
        >
          <span className="detection-shutter-inner" />
        </Button>
        <Button
          type="text"
          className="detection-flip"
          aria-label="Switch camera"
          disabled={cameraStatus !== 'live' || capturing}
          icon={<SyncOutlined />}
          onClick={() =>
            setFacingMode((mode) => (mode === 'environment' ? 'user' : 'environment'))
          }
        />
      </div>
    </div>
  )
}
