import { useCallback, useEffect, useState, type ReactNode } from 'react'
import {
  AppleOutlined,
  ClockCircleOutlined,
  DeleteOutlined,
  EditOutlined,
  FunnelPlotOutlined,
  GoldOutlined,
  LeftOutlined,
  MinusOutlined,
  PlusOutlined,
  RestOutlined,
  RightOutlined,
  ShoppingOutlined,
  SunOutlined,
} from '@ant-design/icons'
import { useSearchParams } from 'react-router-dom'
import {
  App,
  Button,
  Card,
  Empty,
  InputNumber,
  Progress,
  Spin,
  Typography,
} from 'antd'

import { HttpError } from '../../lib/http'
import { useAuth } from '../../hooks/useAuth'
import { MealService } from '../../services/MealService/MealService'
import type { DiaryResponse, MealEntry, MealSlot } from '../../types/meals'
import {
  MEAL_SLOT_LABELS,
  MEAL_SLOTS,
  displayFoodLabel,
  formatFoodNumber,
  formatWeekdayDate,
  localDateString,
  quantityInputWidthPx,
  resolveDiaryDate,
  shiftLocalDateString,
} from '../../types/meals'
import { AddFoodDrawer } from './AddFoodDrawer'
import './tracking.css'

function WaterDropIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      width="1em"
      height="1em"
      fill="currentColor"
      aria-hidden
    >
      <path d="M12 2.2C12 2.2 6 9.1 6 14.2a6 6 0 0 0 12 0C18 9.1 12 2.2 12 2.2z" />
    </svg>
  )
}

const WATER_ML = 250

const GREEN = '#22c55e'
const YELLOW = '#f5b400'
const PURPLE = '#7c3aed'
const BLUE = '#2563eb'

const MACRO_COLORS = {
  protein: GREEN,
  carb: YELLOW,
  fat: PURPLE,
} as const

const SLOT_THEME: Record<
  MealSlot,
  { color: string; background: string; icon: ReactNode }
> = {
  breakfast: { color: YELLOW, background: '#fff7e6', icon: <SunOutlined /> },
  lunch: { color: GREEN, background: '#f6ffed', icon: <RestOutlined /> },
  snacks: { color: PURPLE, background: '#f9f0ff', icon: <ShoppingOutlined /> },
  dinner: { color: BLUE, background: '#e6f4ff', icon: <ClockCircleOutlined /> },
}

function progressPercent(consumed: number, target: number | null): number {
  if (target == null || target <= 0) {
    return 0
  }
  return Math.min(100, Math.round((consumed / target) * 100))
}

function slotCalories(entries: MealEntry[]): number {
  return entries.reduce((sum, entry) => sum + entry.calories, 0)
}

function MacroBar({
  label,
  icon,
  consumed,
  target,
  color,
}: {
  label: string
  icon: ReactNode
  consumed: number
  target: number | null
  color: string
}) {
  return (
    <div className="tracking-macro">
      <div className="tracking-macro-head">
        <span className="tracking-macro-label">
          <span className="tracking-macro-icon" style={{ color }}>
            {icon}
          </span>
          {label}
        </span>
        <Typography.Text type="secondary">
          {formatFoodNumber(consumed, 1)}
          {target != null ? ` / ${formatFoodNumber(target, 1)} g` : ' g'}
        </Typography.Text>
      </div>
      <Progress
        percent={progressPercent(consumed, target)}
        showInfo={false}
        size="small"
        strokeColor={color}
        trailColor={`${color}22`}
      />
    </div>
  )
}

export function TrackingPage() {
  const { profile } = useAuth()
  const { message } = App.useApp()
  const [searchParams, setSearchParams] = useSearchParams()
  const today = localDateString()
  const date = resolveDiaryDate(searchParams.get('date'), today)
  const isToday = date === today
  const [diary, setDiary] = useState<DiaryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [addSlot, setAddSlot] = useState<MealSlot | null>(null)
  const [editEntry, setEditEntry] = useState<MealEntry | null>(null)

  useEffect(() => {
    const raw = searchParams.get('date')
    if (raw == null || raw === date) {
      return
    }
    setSearchParams(date === today ? {} : { date }, { replace: true })
  }, [date, today, searchParams, setSearchParams])

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setDiary(await MealService.getDiary(date))
    } catch (err) {
      setError(err instanceof HttpError ? err.message : "Could not load this day's diary.")
      setDiary(null)
    } finally {
      setLoading(false)
    }
  }, [date])

  useEffect(() => {
    let cancelled = false
    MealService.getDiary(date)
      .then((next) => {
        if (cancelled) {
          return
        }
        setDiary(next)
        setError(null)
        setLoading(false)
      })
      .catch((err: unknown) => {
        if (cancelled) {
          return
        }
        setError(err instanceof HttpError ? err.message : "Could not load this day's diary.")
        setDiary(null)
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [date])

  async function changeQuantity(entry: MealEntry, quantity: number | null) {
    if (quantity == null) {
      return
    }
    if (quantity < 1) {
      await removeMeal(entry.id)
      return
    }
    try {
      await MealService.updateEntry(entry.id, { quantity })
      await load()
    } catch (err) {
      message.error(err instanceof HttpError ? err.message : 'Could not update quantity.')
    }
  }

  function stepQuantity(entry: MealEntry, delta: number) {
    if (delta < 0 && entry.quantity <= 1) {
      void removeMeal(entry.id)
      return
    }
    const next = Math.max(1, Math.round((entry.quantity + delta) * 100) / 100)
    void changeQuantity(entry, next)
  }

  async function removeMeal(id: string) {
    try {
      await MealService.deleteEntry(id)
      await load()
    } catch (err) {
      message.error(err instanceof HttpError ? err.message : 'Could not delete this item.')
    }
  }

  function goToDate(next: string) {
    const clamped = next > today ? today : next
    setSearchParams(clamped === today ? {} : { date: clamped }, { replace: true })
  }

  async function addWater() {
    try {
      await MealService.logWater({ logged_on: date, milliliters: WATER_ML })
      await load()
    } catch (err) {
      message.error(err instanceof HttpError ? err.message : 'Could not log water.')
    }
  }

  async function removeWater(id: string) {
    try {
      await MealService.deleteWater(id)
      await load()
    } catch (err) {
      message.error(err instanceof HttpError ? err.message : 'Could not remove water.')
    }
  }

  function openAdd(slot: MealSlot) {
    setEditEntry(null)
    setAddSlot(slot)
  }

  function openEdit(entry: MealEntry) {
    setAddSlot(null)
    setEditEntry(entry)
  }

  const diaryStale = diary != null && diary.date !== date
  if (diaryStale || (loading && diary == null)) {
    return (
      <div className="tracking-page">
        <Spin />
      </div>
    )
  }

  if (error || diary == null) {
    return (
      <Card className="tracking-page">
        <Typography.Paragraph type="danger">{error}</Typography.Paragraph>
        <Button onClick={() => void load()}>Retry</Button>
      </Card>
    )
  }

  const totals = diary.totals
  const calorieTarget = profile?.target_calories ?? null
  const proteinTarget = profile?.target_protein ?? null
  const carbTarget = profile?.target_carb ?? null
  const fatTarget = profile?.target_fat ?? null

  return (
    <div className="tracking-page">
      <header className="tracking-header">
        <div className="tracking-date-nav">
          <Button
            type="text"
            icon={<LeftOutlined />}
            aria-label="Previous day"
            onClick={() => goToDate(shiftLocalDateString(date, -1))}
          />
          <div className="tracking-date-copy">
            <Typography.Title level={3} className="tracking-today">
              {isToday ? 'Today' : formatWeekdayDate(date)}
            </Typography.Title>
            {isToday ? (
              <Typography.Text type="secondary" className="tracking-date">
                {formatWeekdayDate(date)}
              </Typography.Text>
            ) : null}
          </div>
          <Button
            type="text"
            icon={<RightOutlined />}
            aria-label="Next day"
            disabled={isToday}
            onClick={() => goToDate(shiftLocalDateString(date, 1))}
          />
        </div>
      </header>

      <Card className="tracking-summary" size="small">
        <div className="tracking-summary-row">
          <Progress
            type="circle"
            percent={progressPercent(totals.calories, calorieTarget)}
            size={120}
            strokeColor={GREEN}
            trailColor="#e5e7eb"
            format={() => (
              <div className="tracking-kcal-label">
                <div className="tracking-kcal-value">{formatFoodNumber(totals.calories)} kcal</div>
                <div className="tracking-kcal-of">
                  {calorieTarget != null ? `of ${formatFoodNumber(calorieTarget)} kcal` : 'consumed'}
                </div>
              </div>
            )}
          />
          <div className="tracking-macros">
            <MacroBar
              label="Protein"
              icon={<AppleOutlined />}
              consumed={totals.protein}
              target={proteinTarget}
              color={MACRO_COLORS.protein}
            />
            <MacroBar
              label="Carbs"
              icon={<GoldOutlined />}
              consumed={totals.carb}
              target={carbTarget}
              color={MACRO_COLORS.carb}
            />
            <MacroBar
              label="Fat"
              icon={<FunnelPlotOutlined />}
              consumed={totals.fat}
              target={fatTarget}
              color={MACRO_COLORS.fat}
            />
          </div>
        </div>
      </Card>

      {MEAL_SLOTS.map((slot) => {
        const entries = diary.slots[slot]
        const kcal = slotCalories(entries)
        const theme = SLOT_THEME[slot]
        return (
          <Card
            key={slot}
            className="tracking-slot"
            size="small"
            title={
              <span className="tracking-slot-title">
                <span className="tracking-slot-icon" style={{ color: theme.color, background: theme.background }}>
                  {theme.icon}
                </span>
                <span>{MEAL_SLOT_LABELS[slot]}</span>
                <Typography.Text type="secondary">{formatFoodNumber(kcal)} kcal</Typography.Text>
              </span>
            }
            extra={
              <Button
                type="link"
                size="small"
                className="tracking-add"
                icon={<PlusOutlined />}
                onClick={() => openAdd(slot)}
              >
                Add
              </Button>
            }
          >
            {entries.length === 0 ? (
              <Empty
                className="tracking-empty"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="Nothing logged. Add your first meal."
              >
                <Button type="link" className="tracking-add" icon={<PlusOutlined />} onClick={() => openAdd(slot)}>
                  Add
                </Button>
              </Empty>
            ) : (
              entries.map((entry) => (
                <div key={entry.id} className="tracking-line">
                  <div className="tracking-line-copy">
                    <Typography.Text strong>{displayFoodLabel(entry.label)}</Typography.Text>
                    <Typography.Paragraph type="secondary" className="tracking-line-macros">
                      P {formatFoodNumber(entry.protein, 1)} g · C {formatFoodNumber(entry.carb, 1)} g · F{' '}
                      {formatFoodNumber(entry.fat, 1)} g · {formatFoodNumber(entry.calories)} kcal
                    </Typography.Paragraph>
                    <div
                      className="tracking-qty"
                      role="group"
                      aria-label={`Servings of ${displayFoodLabel(entry.label)}`}
                    >
                      <Button
                        type="text"
                        size="small"
                        icon={<MinusOutlined />}
                        aria-label={`Fewer ${displayFoodLabel(entry.label)}`}
                        onClick={() => stepQuantity(entry, -1)}
                      />
                      <InputNumber
                        min={0.01}
                        step={1}
                        controls={false}
                        value={entry.quantity}
                        style={{ width: quantityInputWidthPx(entry.quantity) }}
                        aria-label={`Servings of ${displayFoodLabel(entry.label)}`}
                        onChange={(value) => void changeQuantity(entry, value)}
                      />
                      <Button
                        type="text"
                        size="small"
                        icon={<PlusOutlined />}
                        aria-label={`More ${displayFoodLabel(entry.label)}`}
                        onClick={() => stepQuantity(entry, 1)}
                      />
                      <span className="tracking-qty-unit">{entry.unit ?? 'servings'}</span>
                    </div>
                  </div>
                  <div className="tracking-line-actions">
                    <Button
                      type="text"
                      icon={<EditOutlined />}
                      aria-label={`Edit ${displayFoodLabel(entry.label)}`}
                      onClick={() => openEdit(entry)}
                    />
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      aria-label={`Remove ${displayFoodLabel(entry.label)}`}
                      onClick={() => void removeMeal(entry.id)}
                    />
                  </div>
                </div>
              ))
            )}
          </Card>
        )
      })}

      <Card
        className="tracking-slot tracking-water"
        size="small"
        title={
          <span className="tracking-slot-title">
            <span className="tracking-slot-icon tracking-water-icon">
              <WaterDropIcon />
            </span>
            <span>Water</span>
            <Typography.Text type="secondary">{diary.water.milliliters} ml</Typography.Text>
          </span>
        }
        extra={
          <Button type="primary" className="tracking-water-add" onClick={() => void addWater()}>
            Add {WATER_ML} ml
          </Button>
        }
      >
        {diary.water.entries.length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No water logged" />
        ) : (
          diary.water.entries.map((entry) => (
            <div key={entry.id} className="tracking-line">
              <Typography.Text>{entry.milliliters} ml</Typography.Text>
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                aria-label="Remove water entry"
                onClick={() => void removeWater(entry.id)}
              />
            </div>
          ))
        )}
      </Card>

      {addSlot ? (
        <AddFoodDrawer
          key={`add-${addSlot}`}
          slot={addSlot}
          date={date}
          onClose={() => setAddSlot(null)}
          onLogged={load}
        />
      ) : null}
      {editEntry ? (
        <AddFoodDrawer
          key={`edit-${editEntry.id}`}
          slot={editEntry.slot}
          date={date}
          entry={editEntry}
          onClose={() => setEditEntry(null)}
          onLogged={load}
        />
      ) : null}
    </div>
  )
}
