"""Cálculos unitarios de recetas usando la unidad base de cada insumo."""

from __future__ import annotations

import math
from typing import Any

from utils.helpers import unit_factor


def ingredient_cost(ingredient: dict[str, Any]) -> float:
    """Costo de una cantidad de receta; `costo_unitario` usa unidad base.

    La cantidad de receta se convierte a mg/ml/unidad con `unit_factor`.
    Valores negativos, no finitos o unidades desconocidas se rechazan para
    impedir que NaN o costos inválidos contaminen totales y recomendaciones.
    """
    try:
        cantidad = float(ingredient["cantidad"])
        costo_unitario = float(ingredient["costo_unitario"])
        factor = unit_factor(ingredient["unidad"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Ingrediente incompleto o con unidad inválida.") from exc
    if not math.isfinite(cantidad) or not math.isfinite(costo_unitario):
        raise ValueError("La cantidad y el costo deben ser números finitos.")
    if cantidad <= 0 or costo_unitario < 0:
        raise ValueError("La cantidad debe ser mayor a cero y el costo no puede ser negativo.")
    return cantidad * factor * costo_unitario


def product_cost(ingredients: list[dict[str, Any]]) -> float:
    """Suma precisa y estable del costo directo de todas las materias primas."""
    return math.fsum(ingredient_cost(item) for item in ingredients)
