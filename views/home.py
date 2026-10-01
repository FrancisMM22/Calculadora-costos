import flet as ft

def home_view(db, go_to):
    raw_count = db.one("SELECT COUNT(*) total FROM materias_primas WHERE activo=1")["total"]
    product_count = db.one("SELECT COUNT(*) total FROM productos WHERE activo=1")["total"]
    def card(title, value, icon, color):
        return ft.Container(content=ft.Row([ft.Icon(icon, size=34, color=color), ft.Column([ft.Text(title, color=ft.Colors.BLUE_GREY_700), ft.Text(str(value), size=30, weight=ft.FontWeight.BOLD)])]), padding=22, border_radius=12, bgcolor=ft.Colors.WHITE, expand=True)
    return ft.Column([ft.Text("Inicio", size=28, weight=ft.FontWeight.BOLD), ft.Text("Resumen de tu calculadora de costos."), ft.Row([card("Materias primas",raw_count,ft.Icons.INVENTORY_2,ft.Colors.BLUE),card("Productos",product_count,ft.Icons.LOCAL_PIZZA,ft.Colors.ORANGE)]), ft.Divider(), ft.Text("Acciones rápidas", size=18, weight=ft.FontWeight.W_600), ft.Row([ft.FilledButton("Agregar materia prima", icon=ft.Icons.ADD, on_click=lambda e: go_to(1, True)),ft.OutlinedButton("Crear producto", icon=ft.Icons.ADD, on_click=lambda e: go_to(2, True))])], spacing=16, expand=True, scroll=ft.ScrollMode.AUTO)
