import type { HeightPayload, WeightPayload, WeightUnit } from '../types/user'

export const KG_PER_LB = 0.45359237

export function convertWeight(value: number, from: WeightUnit, to: WeightUnit): number {
  if (from === to) {
    return value
  }
  if (from === 'lb' && to === 'kg') {
    return roundTo(value * KG_PER_LB, 1)
  }
  return roundTo(value / KG_PER_LB, 1)
}

export function formatHeight(height: HeightPayload | null | undefined): string {
  if (!height) {
    return '—'
  }
  return `${height.feet}'${height.inches}"`
}

export function formatWeight(weight: WeightPayload | null | undefined): string {
  if (!weight) {
    return '—'
  }
  return `${weight.value} ${weight.unit}`
}

function roundTo(value: number, digits: number): number {
  const factor = 10 ** digits
  return Math.round(value * factor) / factor
}
