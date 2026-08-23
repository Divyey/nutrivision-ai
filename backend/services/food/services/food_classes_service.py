"""Legacy 30-class slugs from Flask `class_mapping` (labels only; kcal is not in 004).

The Detect/NMS graph emits training class ids 0–29, the same ids Flask used.
Ultralytics 8.3.73 *metadata* `names` sorts string keys `'0'`…`'29'` alphabetically
({7: '15', 27: '7', …}). That dict is labels for the file header only — do not
remap NMS class ids through it or idli (7) is shown as onion-pakoda (15).
"""

FOOD_CLASS_LABELS: dict[int, str] = {
    0: "aloo-gobi",
    1: "aloo-fry",
    2: "dum-aloo",
    3: "fish-curry",
    4: "ghevar",
    5: "green-chutney",
    6: "gulab-jamun",
    7: "idli",
    8: "jalebi",
    9: "chicken-seekh-kebab",
    10: "kheer",
    11: "kulfi",
    12: "bhature",
    13: "lassi",
    14: "mutton-curry",
    15: "onion-pakoda",
    16: "palak-paneer",
    17: "poha",
    18: "rajma-curry",
    19: "rasmalai",
    20: "samosa",
    21: "shahi-paneer",
    22: "white-rice",
    23: "bhindi-masala",
    24: "chicken-biryani",
    25: "chai",
    26: "chole",
    27: "coconut-chutney",
    28: "dal-tadka",
    29: "dosa",
}


def class_id_for_onnx_index(class_id: int) -> int | None:
    """Training id as emitted by NMS. Do not remap through Ultralytics metadata names."""
    if class_id in FOOD_CLASS_LABELS:
        return class_id
    return None


def label_for_class_id(class_id: int) -> str | None:
    return FOOD_CLASS_LABELS.get(class_id)
