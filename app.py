from pathlib import Path

import flet as ft

from components.sidebar import sidebar
from database.database import Database
from views.home import home_view
from views.materias_primas import materias_primas_view
from views.productos import productos_view


def main(page: ft.Page):
    page.title = "Calculadora de Costos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 0
    page.window_width, page.window_height = 1180, 760
    page.window_min_width, page.window_min_height = 900, 600

    db = Database(Path(__file__).parent / "data" / "costos.db")
    db.initialize()
    state = {"index": 0, "quick_add": False}
    content = ft.Container(expand=True, padding=32)

    def render():
        index, quick = state["index"], state.pop("quick_add", False)
        if index == 0:
            content.content = home_view(db, navigate)
        elif index == 1:
            content.content = materias_primas_view(page, db, render, quick)
        elif index == 2:
            content.content = productos_view(page, db, render, quick)
        else:
            content.content = ft.Column([ft.Text("Configuración", size=28, weight=ft.FontWeight.BOLD), ft.Text("Esta sección estará disponible en una próxima versión.")])
        rail.selected_index = index
        page.update()

    def navigate(index, open_form=False):
        state["index"] = index
        state["quick_add"] = open_form
        render()

    rail = sidebar(0, lambda e: navigate(e.control.selected_index))
    page.add(ft.Row([ft.Container(rail, bgcolor=ft.Colors.WHITE, padding=ft.Padding(top=16, right=0, bottom=0, left=0)), ft.VerticalDivider(width=1), content], expand=True))
    render()


if __name__ == "__main__":
    ft.run(main)
