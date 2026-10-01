import flet as ft


def sidebar(selected_index, on_change):
    return ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=180,
        extended=True,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Inicio"),
            ft.NavigationRailDestination(icon=ft.Icons.INVENTORY_2_OUTLINED, selected_icon=ft.Icons.INVENTORY_2, label="Materias primas"),
            ft.NavigationRailDestination(icon=ft.Icons.LOCAL_PIZZA_OUTLINED, selected_icon=ft.Icons.LOCAL_PIZZA, label="Productos"),
            ft.NavigationRailDestination(icon=ft.Icons.LIGHTBULB_OUTLINE, selected_icon=ft.Icons.LIGHTBULB, label="Costos generales"),
        ],
        on_change=on_change,
    )
