from __future__ import annotations

from datetime import datetime

UNITS = [
    "miligramos",
    "gramos",
    "kilogramos",
    "mililitros",
    "litros",
    "unidad",
]

UNIT_LABELS = {
    "miligramos": "mg",
    "gramos": "g",
    "kilogramos": "kg",
    "mililitros": "ml",
    "litros": "L",
    "unidad": "unidad",
}

RAW_MATERIAL_CATEGORIES = [
    "Harinas",
    "Lácteos",
    "Quesos",
    "Carnes",
    "Fiambres",
    "Verduras",
    "Frutas",
    "Aceites",
    "Condimentos",
    "Salsas",
    "Conservas",
    "Panificados",
    "Huevos",
    "Helados",
    "Bebidas",
    "Cervezas",
    "Otros",
]

PRODUCT_CATEGORIES = [
    "Pizzas",
    "Empanadas",
    "Tartas",
    "Focaccia",
    "Bebidas",
    "Postres",
    "Combos",
    "Otros",
]

UNIT_INFO = {
    "miligramos": ("peso", 0.001, "gramo"),
    "gramos": ("peso", 1.0, "gramo"),
    "kilogramos": ("peso", 1000.0, "gramo"),
    "mililitros": ("volumen", 1.0, "mililitro"),
    "litros": ("volumen", 1000.0, "mililitro"),
    "unidad": ("unidad", 1.0, "unidad"),
}


def to_number(value: object) -> float:
    """Parse decimal values without confusing a decimal point with thousands."""
    text = str(value).strip().replace("$", "").replace(" ", "")

    if not text:
        raise ValueError("empty number")

    if "," in text and "." in text:
        # The rightmost separator is the decimal separator.
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")

    elif "," in text:
        text = text.replace(",", ".")

    elif text.count(".") > 1 or (
        text.count(".") == 1
        and len(text.rsplit(".", 1)[1]) == 3
    ):
        text = text.replace(".", "")

    return float(text)


def unit_factor(unit: str) -> float:
    return UNIT_INFO[unit][1]


def unit_family(unit: str) -> str:
    return UNIT_INFO[unit][0]


def base_unit(unit: str) -> str:
    return UNIT_INFO[unit][2]


def compatible_units(unit: str) -> list[str]:
    return [
        name
        for name in UNITS
        if unit_family(name) == unit_family(unit)
    ]


def money(value: float) -> str:
    return (
        "$ "
        + f"{round(value, 2):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def now() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")
