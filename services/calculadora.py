from utils.helpers import unit_factor

def ingredient_cost(ingredient: dict) -> float:
    return float(ingredient["cantidad"]) * unit_factor(ingredient["unidad"]) * float(ingredient["costo_unitario"])

def product_cost(ingredients: list[dict]) -> float:
    return sum(ingredient_cost(item) for item in ingredients)
