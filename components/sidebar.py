import flet as ft

from components.branding import CHARCOAL, PIZZA_RED


def sidebar(selected_index, on_change):
    return ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=112,
        min_extended_width=210,
        extended=True,
        group_alignment=-0.9,
        bgcolor=ft.Colors.WHITE,
        indicator_color="#FCE8E5",
        indicator_shape=ft.RoundedRectangleBorder(radius=12),
        selected_label_text_style=ft.TextStyle(color=PIZZA_RED, weight=ft.FontWeight.BOLD),
        unselected_label_text_style=ft.TextStyle(color=CHARCOAL),
        use_indicator=True,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD_ROUNDED, selected_icon=ft.Icons.DASHBOARD_ROUNDED, label="Inicio"),
            ft.NavigationRailDestination(icon=ft.Icons.INVENTORY_2_ROUNDED, selected_icon=ft.Icons.INVENTORY_2_ROUNDED, label="Materias primas"),
            ft.NavigationRailDestination(icon=ft.Icons.LOCAL_PIZZA_ROUNDED, selected_icon=ft.Icons.LOCAL_PIZZA_ROUNDED, label="Productos / Recetas"),
            ft.NavigationRailDestination(icon=ft.Icons.ATTACH_MONEY_ROUNDED, selected_icon=ft.Icons.ATTACH_MONEY_ROUNDED, label="Costos generales"),
            ft.NavigationRailDestination(icon=ft.Icons.ANALYTICS_ROUNDED, selected_icon=ft.Icons.ANALYTICS_ROUNDED, label="Estrategia de precios"),
        ],
        on_change=on_change,
    )
