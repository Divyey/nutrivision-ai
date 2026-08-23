CM_PER_INCH = 2.54
INCHES_PER_FOOT = 12
KG_PER_LB = 0.45359237
MALE_BMR_OFFSET = 5
FEMALE_BMR_OFFSET = -161
UNSPECIFIED_BMR_OFFSET = (MALE_BMR_OFFSET + FEMALE_BMR_OFFSET) / 2

# Mifflin–St Jeor is sex-specific (+5 male / −161 female). There is no validated
# formula for unspecified sex, so we use the midpoint of those two constants.


def height_to_cm(feet: int, inches: int) -> float:
    return round((feet * INCHES_PER_FOOT + inches) * CM_PER_INCH, 2)


def cm_to_height(cm: float) -> tuple[int, int]:
    total_inches = int(round(float(cm) / CM_PER_INCH))
    feet, inches = divmod(total_inches, INCHES_PER_FOOT)
    if inches == INCHES_PER_FOOT:
        feet += 1
        inches = 0
    return feet, inches


def weight_to_kg(value: float, unit: str) -> float:
    if unit == "lb":
        return round(float(value) * KG_PER_LB, 2)
    if unit == "kg":
        return round(float(value), 2)
    raise ValueError("weight unit must be kg or lb")


def bmr_sex_offset(gender: str) -> float:
    if gender == "male":
        return MALE_BMR_OFFSET
    if gender == "female":
        return FEMALE_BMR_OFFSET
    if gender == "unspecified":
        return UNSPECIFIED_BMR_OFFSET
    raise ValueError("gender must be male, female, or unspecified")
