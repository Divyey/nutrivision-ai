export type Gender = 'male' | 'female' | 'unspecified'

export type ActivityLevel =
  | 'sedentary'
  | 'lightly_active'
  | 'moderately_active'
  | 'very_active'
  | 'extra_active'

export type VeganStatus = 'yes' | 'no'

export type Allergy = 'none' | 'lactose' | 'gluten' | 'nuts_beans' | 'eggs'

export type WeightUnit = 'kg' | 'lb'

export type HeightPayload = {
  feet: number
  inches: number
}

export type WeightPayload = {
  value: number
  unit: WeightUnit
}

export type UserProfile = {
  id: string
  name: string
  email: string
  age: number | null
  gender: Gender | null
  weight: WeightPayload | null
  height: HeightPayload | null
  activity_level: ActivityLevel | null
  vegan: VeganStatus | null
  allergy: Allergy | null
  status: string | null
  start_date: string | null
  target_calories: number | null
  target_protein: number | null
  target_carb: number | null
  target_fat: number | null
  target_bmi: number | null
}

export type UpdateProfileRequest = {
  age?: number
  gender?: Gender
  weight?: WeightPayload
  height?: HeightPayload
  activity_level?: ActivityLevel
  vegan?: VeganStatus
  allergy?: Allergy
}

export const ACTIVITY_OPTIONS: { value: ActivityLevel; label: string }[] = [
  { value: 'sedentary', label: 'Sedentary (little or no exercise)' },
  {
    value: 'lightly_active',
    label: 'Lightly active (light exercise/sports 1-3 days/week)',
  },
  {
    value: 'moderately_active',
    label: 'Moderately active (moderate exercise/sports 3-5 days/week)',
  },
  {
    value: 'very_active',
    label: 'Very active (hard exercise/sports 6-7 days a week)',
  },
  {
    value: 'extra_active',
    label: 'Extra active (very hard exercise/sports and a physical job)',
  },
]

export const GENDER_OPTIONS: { value: Gender; label: string }[] = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'unspecified', label: 'Not specified' },
]

export const VEGAN_OPTIONS: { value: VeganStatus; label: string }[] = [
  { value: 'no', label: 'No' },
  { value: 'yes', label: 'Yes' },
]

export const ALLERGY_OPTIONS: { value: Allergy; label: string }[] = [
  { value: 'none', label: 'None' },
  { value: 'lactose', label: 'Lactose' },
  { value: 'gluten', label: 'Gluten' },
  { value: 'nuts_beans', label: 'Nuts/Beans' },
  { value: 'eggs', label: 'Eggs' },
]

export const WEIGHT_UNIT_OPTIONS: { value: WeightUnit; label: string }[] = [
  { value: 'kg', label: 'kg' },
  { value: 'lb', label: 'lb' },
]

export function isProfileComplete(profile: UserProfile | null): boolean {
  return (
    profile != null &&
    profile.age != null &&
    profile.gender != null &&
    profile.weight != null &&
    profile.height != null &&
    profile.activity_level != null
  )
}

export function optionLabel(
  options: { value: string; label: string }[],
  value: string | null | undefined,
): string {
  if (value == null) {
    return '—'
  }
  return options.find((option) => option.value === value)?.label ?? value
}

export function profileToFormValues(profile: UserProfile): UpdateProfileRequest {
  return {
    age: profile.age ?? undefined,
    gender: profile.gender ?? undefined,
    weight: profile.weight ?? undefined,
    height: profile.height ?? undefined,
    activity_level: profile.activity_level ?? undefined,
    vegan: profile.vegan ?? undefined,
    allergy: profile.allergy ?? undefined,
  }
}
