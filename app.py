from pathlib import Path

import flet as ft

from components.sidebar import sidebar
from components.branding import CHARCOAL, DOUGH_CREAM, PIZZA_RED, WHITE
from database.database import Database
from views.costos_generales import costos_generales_view
from views.home import home_view
from views.materias_primas import materias_primas_view
from views.productos import productos_view
from views.recomendador_precios import recomendador_precios_view


def main(page: ft.Page):
    page.title = "Pizzería Los Tilos | Gestión de Costos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = {
        "BrandFont": "https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(
        color_scheme_seed=PIZZA_RED,
        font_family="BrandFont",
        use_material3=True,
    )
    page.bgcolor = DOUGH_CREAM
    page.padding = 0
    page.window_width, page.window_height = 1180, 760
    page.window_min_width, page.window_min_height = 900, 600

    db = Database(Path(__file__).parent / "data" / "costos.db")
    db.initialize()
    state = {"index": 0, "quick_add": False}
    content = ft.Container(expand=True, padding=24)

    def render():
        index, quick = state["index"], state.pop("quick_add", False)
        if index == 0:
            content.content = home_view(db, navigate)
        elif index == 1:
            content.content = materias_primas_view(page, db, render, quick)
        elif index == 2:
            content.content = productos_view(page, db, render, quick)
        elif index == 3:
            content.content = costos_generales_view(page, db, render, quick)
        elif index == 4:
            content.content = recomendador_precios_view(page, db)
        rail.selected_index = index
        page.update()

    def navigate(index, open_form=False):
        state["index"] = index
        state["quick_add"] = open_form
        render()

    rail = sidebar(0, lambda e: navigate(e.control.selected_index))
    topbar = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    ft.Icon(ft.Icons.LOCAL_PIZZA_ROUNDED, color=WHITE, size=26),
                    bgcolor=PIZZA_RED, width=46, height=46,
                    border_radius=ft.BorderRadius.all(14),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column(
                    [
                        ft.Text("Pizzería Los Tilos", size=22, weight=ft.FontWeight.BOLD, color=PIZZA_RED, font_family="BrandFont"),
                        ft.Text("Sistema de Gestión de Costos y Estrategia de Precios", size=12, color=CHARCOAL),
                    ], spacing=1,
                ),
            ], spacing=12,
        ),
        bgcolor=WHITE, padding=ft.Padding(24, 14, 24, 14),
        border=ft.Border(bottom=ft.BorderSide(1, "#E8DED4")),
    )
    workspace = ft.Row(
        [
            ft.Container(rail, bgcolor=WHITE, padding=ft.Padding(8, 12, 8, 8)),
            ft.VerticalDivider(width=1, color="#E8DED4"),
            content,
        ], expand=True, spacing=0,
    )
    page.add(ft.Column([topbar, workspace], expand=True, spacing=0))
    render()


if __name__ == "__main__":
    ft.run(main)
