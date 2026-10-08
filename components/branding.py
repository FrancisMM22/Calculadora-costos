"""Identidad visual compartida de Pizzería Los Tilos."""

import flet as ft

PIZZA_RED = "#C0392B"
CHEESE_GOLD = "#F39C12"
DOUGH_CREAM = "#FDFBF7"
CHARCOAL = "#2C3E50"
WHITE = "#FFFFFF"
SOFT_BORDER = "#E8DED4"


def page_heading(title: str, subtitle: str) -> ft.Control:
    return ft.Column(
        [
            ft.Text(title, size=28, weight=ft.FontWeight.BOLD, color=CHARCOAL),
            ft.Text(subtitle, color="#667085"),
            ft.Container(width=72, height=4, bgcolor=CHEESE_GOLD, border_radius=4),
        ],
        spacing=6,
    )


def soft_shadow() -> ft.BoxShadow:
    return ft.BoxShadow(blur_radius=12, spread_radius=0, color="#1A2C3E50", offset=ft.Offset(0, 3))
