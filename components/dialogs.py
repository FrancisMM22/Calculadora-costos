import flet as ft

def show_dialog(page: ft.Page, dialog: ft.AlertDialog):
    page.show_dialog(dialog)

def close_dialog(page: ft.Page, dialog: ft.AlertDialog):
    page.pop_dialog()

def confirm(page, title, message, on_confirm):
    dialog = ft.AlertDialog(modal=True, title=ft.Text(title), content=ft.Text(message), actions_alignment=ft.MainAxisAlignment.END)
    dialog.actions = [ft.TextButton("Cancelar", on_click=lambda e: close_dialog(page, dialog)), ft.FilledButton("Eliminar", on_click=lambda e: (close_dialog(page, dialog), on_confirm()))]
    show_dialog(page, dialog)
