import flet as ft

def action_buttons(on_edit, on_delete):
    return ft.Row([ft.IconButton(ft.Icons.EDIT_OUTLINED, tooltip="Editar", on_click=on_edit), ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Eliminar", icon_color=ft.Colors.RED_400, on_click=on_delete)], spacing=0)

def simple_table(columns, rows):
    return ft.DataTable(columns=[ft.DataColumn(ft.Text(c)) for c in columns], rows=rows, heading_row_color=ft.Colors.BLUE_GREY_50, border=ft.Border.all(1, ft.Colors.BLUE_GREY_100), border_radius=ft.BorderRadius.all(8))
