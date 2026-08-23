import { ArrowLeftOutlined } from '@ant-design/icons'
import { Button, List, Tag, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'

import type { FoodBox, FoodPredictItem, FoodPredictResponse } from '../../types/detection'

type ResultsPhaseProps = {
  previewUrl: string
  payload: FoodPredictResponse
  onRetake: () => void
}

function displayLabel(slug: string): string {
  return slug
    .split('-')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function boxStyle(box: FoodBox, imageWidth: number, imageHeight: number) {
  return {
    left: `${(box.x1 / imageWidth) * 100}%`,
    top: `${(box.y1 / imageHeight) * 100}%`,
    width: `${((box.x2 - box.x1) / imageWidth) * 100}%`,
    height: `${((box.y2 - box.y1) / imageHeight) * 100}%`,
  }
}

export function ResultsPhase({ previewUrl, payload, onRetake }: ResultsPhaseProps) {
  const navigate = useNavigate()
  const empty = payload.items.length === 0

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
      <div className="detection-stage detection-stage-results">
        <div className="detection-results-frame">
          <img className="detection-image-contain" src={previewUrl} alt="Analyzed meal" />
          {payload.items.map((item, index) => (
            <div
              key={`${item.class_id}-${index}`}
              className="detection-box"
              style={boxStyle(item.box, payload.image_width, payload.image_height)}
            >
              <span className="detection-box-caption">
                {displayLabel(item.label)} {Math.round(item.confidence * 100)}%
              </span>
            </div>
          ))}
        </div>
      </div>
      <div className="detection-footer">
        <Typography.Title level={4} style={{ marginBottom: 4 }}>
          Results
        </Typography.Title>
        {empty ? (
          <Typography.Paragraph className="detection-subtitle">
            No dishes detected.
          </Typography.Paragraph>
        ) : (
          <List
            className="detection-results-list"
            dataSource={payload.items}
            renderItem={(item: FoodPredictItem) => (
              <List.Item>
                <Typography.Text>{displayLabel(item.label)}</Typography.Text>
                <Tag>{Math.round(item.confidence * 100)}%</Tag>
              </List.Item>
            )}
          />
        )}
        <div className="detection-actions">
          <Button color="green" variant="solid" size="large" block onClick={onRetake}>
            Take another photo
          </Button>
        </div>
      </div>
    </div>
  )
}
