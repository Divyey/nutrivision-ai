import { useEffect, useState } from 'react'
import { CameraOutlined } from '@ant-design/icons'
import { App, Button, Drawer, Input, InputNumber, List, Select, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'

import { HttpError, isAbortError } from '../../lib/http'
import { MealService } from '../../services/MealService/MealService'
import { NutritionService } from '../../services/NutritionService/NutritionService'
import {
  MEAL_SLOT_LABELS,
  displayFoodLabel,
  formatFoodNumber,
  quantityInputWidthPx,
  type MealEntry,
  type MealSlot,
} from '../../types/meals'
import {
  defaultServing,
  estimatedCalories,
  type FoodSearchHit,
} from '../../types/nutrition'

type AddFoodDrawerProps = {
  slot: MealSlot
  date: string
  onClose: () => void
  onLogged: () => Promise<void>
  entry?: MealEntry
}

export function AddFoodDrawer({ slot, date, onClose, onLogged, entry }: AddFoodDrawerProps) {
  const { message } = App.useApp()
  const navigate = useNavigate()
  const editing = entry != null
  const [query, setQuery] = useState('')
  const [hits, setHits] = useState<FoodSearchHit[]>([])
  const [searching, setSearching] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)
  const [selected, setSelected] = useState<FoodSearchHit | null>(null)
  const [unit, setUnit] = useState<string | null>(entry?.unit ?? null)
  const [quantity, setQuantity] = useState(entry?.quantity ?? 1)
  const [saving, setSaving] = useState(false)
  const [loadingFood, setLoadingFood] = useState(editing && entry.food_id != null)
  const needle = query.trim()
  const showHits = needle.length >= 2

  useEffect(() => {
    if (entry?.food_id == null) {
      return
    }
    const controller = new AbortController()
    NutritionService.get(entry.food_id, controller.signal)
      .then((hit) => {
        setSelected(hit)
        setUnit(entry.unit ?? defaultServing(hit)?.unit ?? null)
      })
      .catch((err: unknown) => {
        if (isAbortError(err)) {
          return
        }
        message.error(err instanceof HttpError ? err.message : 'Could not load this food.')
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoadingFood(false)
        }
      })
    return () => {
      controller.abort()
    }
  }, [entry, message])

  useEffect(() => {
    if (needle.length < 2) {
      return
    }
    const controller = new AbortController()
    const timer = window.setTimeout(() => {
      setSearching(true)
      NutritionService.search(needle, controller.signal)
        .then((result) => {
          setHits(result.items)
          setSearchError(null)
        })
        .catch((err: unknown) => {
          if (isAbortError(err)) {
            return
          }
          setHits([])
          setSearchError(err instanceof HttpError ? err.message : 'Could not search foods.')
        })
        .finally(() => {
          if (!controller.signal.aborted) {
            setSearching(false)
          }
        })
    }, 250)
    return () => {
      window.clearTimeout(timer)
      controller.abort()
    }
  }, [needle])

  function pickHit(hit: FoodSearchHit) {
    setSelected(hit)
    setUnit(defaultServing(hit)?.unit ?? null)
    if (!editing) {
      setQuantity(1)
    }
  }

  async function save() {
    if (selected != null && unit == null) {
      return
    }
    if (!editing && (selected == null || unit == null)) {
      return
    }
    setSaving(true)
    try {
      if (editing) {
        if (selected != null && unit != null) {
          await MealService.updateEntry(entry.id, {
            food_id: selected.id,
            unit,
            quantity,
          })
        } else {
          await MealService.updateEntry(entry.id, { quantity })
        }
        message.success(`Updated ${selected?.name ?? displayFoodLabel(entry.label)}`)
      } else if (selected != null && unit != null) {
        await MealService.logEntries({
          logged_on: date,
          slot,
          items: [{ food_id: selected.id, unit, quantity }],
        })
        message.success(`Added ${selected.name}`)
      }
      await onLogged()
      onClose()
    } catch (err) {
      message.error(
        err instanceof HttpError ? err.message : editing ? 'Could not update this food.' : 'Could not log this food.',
      )
    } finally {
      setSaving(false)
    }
  }

  const kcal = selected != null && unit != null ? estimatedCalories(selected, unit, quantity) : null
  const emptyHint = needle.length < 2 ? 'Type at least 2 letters.' : (searchError ?? 'No matching foods.')
  const canSave = selected == null ? editing : unit != null
  const title = editing ? `Edit ${displayFoodLabel(entry.label)}` : `Add to ${MEAL_SLOT_LABELS[slot]}`
  const foodName = selected?.name ?? displayFoodLabel(entry?.label ?? '')

  return (
    <Drawer
      title={title}
      placement="bottom"
      height="88%"
      open
      onClose={onClose}
      destroyOnHidden
      extra={
        editing ? undefined : (
          <Button
            type="text"
            icon={<CameraOutlined />}
            onClick={() => navigate(`/detect?slot=${slot}&date=${date}`)}
          >
            Scan
          </Button>
        )
      }
    >
      <Input.Search
        allowClear
        autoFocus={!editing}
        placeholder="Search idli, roti, dal…"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        aria-label="Search foods"
      />
      {selected != null || editing ? (
        <div className="tracking-food-log">
          <Typography.Text strong>{foodName}</Typography.Text>
          <div className="tracking-food-log-row">
            <InputNumber
              min={0.01}
              step={1}
              value={quantity}
              style={{ width: quantityInputWidthPx(quantity) }}
              aria-label={`Quantity of ${foodName}`}
              onChange={(value) => {
                if (value != null) {
                  setQuantity(value)
                }
              }}
            />
            {selected != null ? (
              <Select
                value={unit ?? undefined}
                aria-label="Serving unit"
                style={{ minWidth: 140 }}
                options={selected.servings.map((row) => ({
                  value: row.unit,
                  label: row.unit,
                }))}
                onChange={setUnit}
              />
            ) : (
              <span className="tracking-qty-unit">{entry?.unit ?? 'servings'}</span>
            )}
          </div>
          {kcal != null ? (
            <Typography.Text type="secondary">About {formatFoodNumber(kcal)} kcal</Typography.Text>
          ) : null}
          <Button type="primary" block loading={saving} disabled={!canSave} onClick={() => void save()}>
            {editing ? 'Save' : 'Log food'}
          </Button>
        </div>
      ) : null}
      {showHits || !editing ? (
        <List
          className="tracking-food-list"
          loading={(searching && showHits) || loadingFood}
          dataSource={showHits ? hits : []}
          locale={{ emptyText: emptyHint }}
          renderItem={(hit) => (
            <List.Item
              className={
                selected?.id === hit.id ? 'tracking-food-hit tracking-food-hit-active' : 'tracking-food-hit'
              }
              onClick={() => pickHit(hit)}
            >
              <List.Item.Meta
                title={hit.name}
                description={
                  hit.calories_per_100g != null
                    ? `${hit.calories_per_100g.toFixed(0)} kcal / 100 g`
                    : undefined
                }
              />
            </List.Item>
          )}
        />
      ) : null}
    </Drawer>
  )
}
