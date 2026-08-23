import { useMemo, useState, type ReactNode } from 'react'
import {
  ArrowLeftOutlined,
  ArrowRightOutlined,
  CameraOutlined,
  CheckCircleFilled,
  CheckOutlined,
  CoffeeOutlined,
  FireOutlined,
  LockOutlined,
  MinusOutlined,
  MoonOutlined,
  PlusOutlined,
  SunOutlined,
} from '@ant-design/icons'
import { App, Button, Typography } from 'antd'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { HttpError } from '../../lib/http'
import { MealService } from '../../services/MealService/MealService'
import type { FoodBox, FoodPredictItem, FoodPredictResponse } from '../../types/detection'
import {
  MEAL_SLOT_LABELS,
  MEAL_SLOTS,
  displayFoodLabel,
  isMealSlot,
  resolveDiaryDate,
  type MealSlot,
} from '../../types/meals'

type ResultsPhaseProps = {
  previewUrl: string
  payload: FoodPredictResponse
  onRetake: () => void
}

type DishDraft = {
  class_id: number
  label: string
  quantity: number
  confidence: number
}

const SLOT_ICONS: Record<MealSlot, ReactNode> = {
  breakfast: <CoffeeOutlined />,
  lunch: <SunOutlined />,
  snacks: <FireOutlined />,
  dinner: <MoonOutlined />,
}

function boxStyle(box: FoodBox, imageWidth: number, imageHeight: number) {
  return {
    left: `${(box.x1 / imageWidth) * 100}%`,
    top: `${(box.y1 / imageHeight) * 100}%`,
    width: `${((box.x2 - box.x1) / imageWidth) * 100}%`,
    height: `${((box.y2 - box.y1) / imageHeight) * 100}%`,
  }
}

function dishesFromItems(items: FoodPredictItem[]): DishDraft[] {
  const byClass = new Map<number, DishDraft>()
  for (const item of items) {
    const current = byClass.get(item.class_id)
    if (current) {
      current.quantity += 1
      current.confidence = Math.max(current.confidence, item.confidence)
    } else {
      byClass.set(item.class_id, {
        class_id: item.class_id,
        label: item.label,
        quantity: 1,
        confidence: item.confidence,
      })
    }
  }
  return [...byClass.values()]
}

function confidenceCopy(confidence: number): string {
  if (confidence >= 0.75) {
    return 'High confidence'
  }
  if (confidence >= 0.5) {
    return 'Medium confidence'
  }
  return 'Lower confidence'
}

export function ResultsPhase({ previewUrl, payload, onRetake }: ResultsPhaseProps) {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { message } = App.useApp()
  const initialDishes = useMemo(() => dishesFromItems(payload.items), [payload.items])
  const slotParam = searchParams.get('slot')
  const loggedOn = resolveDiaryDate(searchParams.get('date'))
  const [slot, setSlot] = useState<MealSlot>(isMealSlot(slotParam) ? slotParam : 'lunch')
  const [dishes, setDishes] = useState<DishDraft[]>(initialDishes)
  const [logging, setLogging] = useState(false)
  const empty = dishes.length === 0
  const loggable = dishes.filter((dish) => dish.quantity >= 1)
  const detectionCount = payload.items.length

  function changeQuantity(classId: number, delta: number) {
    setDishes((rows) =>
      rows.map((row) =>
        row.class_id === classId
          ? { ...row, quantity: Math.min(99, Math.max(1, row.quantity + delta)) }
          : row,
      ),
    )
  }

  async function confirmAndLog() {
    if (loggable.length === 0) {
      return
    }
    setLogging(true)
    try {
      await MealService.logEntries({
        logged_on: loggedOn,
        slot,
        items: loggable.map((dish) => ({
          class_id: dish.class_id,
          quantity: dish.quantity,
        })),
      })
      message.success('Logged to your diary')
      navigate(`/tracking?date=${loggedOn}`)
    } catch (error) {
      const text =
        error instanceof HttpError
          ? error.message
          : 'Could not log this meal. Nutrition data may be missing.'
      message.error(text)
    } finally {
      setLogging(false)
    }
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
        <Typography.Title level={4} className="detection-heading">
          Scan Results
        </Typography.Title>
        <span className="detection-top-spacer" />
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
                {displayFoodLabel(item.label)} {Math.round(item.confidence * 100)}%
              </span>
            </div>
          ))}
        </div>
      </div>
      <div className="detection-footer">
        {empty ? (
          <Typography.Paragraph className="detection-subtitle">
            No dishes detected.
          </Typography.Paragraph>
        ) : (
          <>
            <div className="detection-summary">
              <CheckCircleFilled className="detection-summary-icon" />
              <div>
                <Typography.Text strong>
                  {detectionCount} {detectionCount === 1 ? 'dish' : 'dishes'} detected
                </Typography.Text>
                <Typography.Paragraph className="detection-subtitle detection-summary-copy">
                  Review and confirm before logging.
                </Typography.Paragraph>
              </div>
            </div>
            {dishes.map((dish) => (
              <div key={dish.class_id} className="detection-dish">
                <div className="detection-dish-copy">
                  <Typography.Text strong>{displayFoodLabel(dish.label)}</Typography.Text>
                  <Typography.Paragraph className="detection-dish-confidence">
                    {confidenceCopy(dish.confidence)}
                  </Typography.Paragraph>
                </div>
                <div className="detection-qty" role="group" aria-label={`Servings of ${displayFoodLabel(dish.label)}`}>
                  <Button
                    type="text"
                    size="small"
                    icon={<MinusOutlined />}
                    aria-label={`Fewer ${displayFoodLabel(dish.label)}`}
                    disabled={dish.quantity <= 1}
                    onClick={() => changeQuantity(dish.class_id, -1)}
                  />
                  <span className="detection-qty-value">{dish.quantity}</span>
                  <Button
                    type="text"
                    size="small"
                    icon={<PlusOutlined />}
                    aria-label={`More ${displayFoodLabel(dish.label)}`}
                    disabled={dish.quantity >= 99}
                    onClick={() => changeQuantity(dish.class_id, 1)}
                  />
                </div>
              </div>
            ))}
            <Typography.Paragraph className="detection-subtitle">Add to</Typography.Paragraph>
            <div className="detection-slot-grid" role="radiogroup" aria-label="Meal">
              {MEAL_SLOTS.map((value) => {
                const selected = slot === value
                return (
                  <button
                    key={value}
                    type="button"
                    role="radio"
                    aria-checked={selected}
                    className={
                      selected
                        ? 'detection-slot-btn detection-slot-btn-active'
                        : 'detection-slot-btn'
                    }
                    onClick={() => setSlot(value)}
                  >
                    <span className="detection-slot-icon">{SLOT_ICONS[value]}</span>
                    {MEAL_SLOT_LABELS[value]}
                  </button>
                )
              })}
            </div>
          </>
        )}
        <div className="detection-actions">
          <Button
            color="green"
            variant="solid"
            size="large"
            block
            disabled={empty || loggable.length === 0}
            loading={logging}
            onClick={() => void confirmAndLog()}
          >
            <CheckOutlined />
            Confirm & Log
            <ArrowRightOutlined />
          </Button>
          <Button size="large" block icon={<CameraOutlined />} onClick={onRetake}>
            Take another photo
          </Button>
        </div>
        <p className="detection-privacy">
          <LockOutlined /> Your data is private and secure
        </p>
      </div>
    </div>
  )
}
