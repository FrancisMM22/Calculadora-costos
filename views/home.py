import flet as ft

from components.branding import CHEESE_GOLD, PIZZA_RED, WHITE, page_heading, soft_shadow


def home_view(db, go_to):
    raw_count = db.one("SELECT COUNT(*) total FROM materias_primas WHERE activo=1")["total"]
    product_count = db.one("SELECT COUNT(*) total FROM productos WHERE activo=1")["total"]

    def card(title, value, icon, color):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(ft.Icon(icon, size=30, color=WHITE), bgcolor=color,
                                 width=56, height=56, border_radius=16,
                                 alignment=ft.Alignment(0, 0)),
                    ft.Column([ft.Text(title, color="#667085"),
                               ft.Text(str(value), size=30, weight=ft.FontWeight.BOLD,
                                       color="#2C3E50")], spacing=2),
                ], spacing=16,
            ),
            padding=22, border_radius=12, bgcolor=WHITE, expand=True,
            shadow=soft_shadow(),
        )

    return ft.Column(
        [
            page_heading("Inicio", "Resumen de costos y actividad de Pizzería Los Tilos."),
            ft.Row(
                [
                    card("Materias primas activas", raw_count, ft.Icons.INVENTORY_2_ROUNDED, PIZZA_RED),
                    card("Productos del catálogo", product_count, ft.Icons.LOCAL_PIZZA_ROUNDED, CHEESE_GOLD),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=18,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Acciones rápidas", size=19, weight=ft.FontWeight.BOLD, color="#2C3E50"),
                        ft.Text("Mantené actualizados tus insumos y recetas para obtener recomendaciones precisas."),
                        ft.Row(
                            [
                                ft.FilledButton("Agregar materia prima", icon=ft.Icons.ADD,
                                                on_click=lambda e: go_to(1, True)),
                                ft.OutlinedButton("Crear producto", icon=ft.Icons.ADD,
                                                  on_click=lambda e: go_to(2, True)),
                                ft.OutlinedButton("Ver estrategia de precios", icon=ft.Icons.ANALYTICS_ROUNDED,
                                                  on_click=lambda e: go_to(4)),
                            ], wrap=True, spacing=10,
                        ),
                    ], spacing=12,
                ),
                bgcolor=WHITE, padding=22, border_radius=12, shadow=soft_shadow(),
            ),
        ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO,
    )
