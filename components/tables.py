import flet as ft

from components.branding import PIZZA_RED, SOFT_BORDER

def action_buttons(on_edit, on_delete):
    return ft.Row([ft.IconButton(ft.Icons.EDIT_OUTLINED, tooltip="Editar", icon_color=PIZZA_RED, on_click=on_edit), ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Eliminar", icon_color=ft.Colors.RED_400, on_click=on_delete)], spacing=0)

def simple_table(columns, rows):
    striped_rows = [
        ft.DataRow(cells=row.cells, color="#FFF8F2" if index % 2 else ft.Colors.WHITE,
                   selected=row.selected, on_long_press=row.on_long_press,
                   on_select_change=row.on_select_change)
        for index, row in enumerate(rows)
    ]
    return ft.DataTable(
        columns=[ft.DataColumn(ft.Text(c, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)) for c in columns],
        rows=striped_rows,
        heading_row_color=PIZZA_RED,
        border=ft.Border.all(1, SOFT_BORDER),
        border_radius=ft.BorderRadius.all(10),
        divider_thickness=1,
        horizontal_margin=14,
        column_spacing=20,
    )
