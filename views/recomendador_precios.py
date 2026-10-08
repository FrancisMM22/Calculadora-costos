"""Panel de precios, márgenes y rendimiento del catálogo."""

from __future__ import annotations

import flet as ft

from components.tables import simple_table
from components.branding import CHEESE_GOLD, PIZZA_RED, WHITE, page_heading, soft_shadow
from services.analisis import analizar_catalogo, actualizar_precio_actual
from utils.helpers import money, to_number


def recomendador_precios_view(page: ft.Page, db) -> ft.Control:
    margen = ft.Slider(min=0, max=100, divisions=20, value=30, label="{value}%")
    margen_texto = ft.Text("Recargo sobre costo: 30%", weight=ft.FontWeight.W_600)
    estado_error = ft.Text(color=ft.Colors.RED_600)
    dashboard = ft.Column(spacing=16)
    precios: dict[int, ft.TextField] = {}

    def tarjeta(titulo: str, valor: str, detalle: str = "") -> ft.Control:
        return ft.Container(
            content=ft.Column([ft.Text(titulo, color=ft.Colors.BLUE_GREY_700),
                               ft.Text(valor, size=22, weight=ft.FontWeight.BOLD),
                               ft.Text(detalle, size=12, color=ft.Colors.BLUE_GREY_600)]),
            bgcolor=WHITE, padding=18, border_radius=12, expand=True, shadow=soft_shadow(),
        )

    def build(e=None):
        try:
            margen_texto.value = f"Recargo sobre costo: {margen.value:.0f}%"
            analisis = analizar_catalogo(db, margen.value or 0)
            valores_previos = {product_id: field.value for product_id, field in precios.items()}
            precios.clear()
            if not analisis:
                dashboard.controls = [ft.Container(ft.Text("Todavía no hay productos para analizar. Creá productos y agregales ingredientes para obtener recomendaciones."), bgcolor=ft.Colors.WHITE, padding=24, border_radius=10)]
                estado_error.value = ""
                page.update()
                return

            valores_actuales = {}
            for item in analisis:
                field = ft.TextField(label="Precio actual", prefix=ft.Text("$ "), width=150,
                                     keyboard_type=ft.KeyboardType.NUMBER, dense=True,
                                     value=valores_previos.get(item["id"], ""))
                precios[item["id"]] = field
                valores_actuales[item["id"]] = field

            def actualizar(e=None):
                try:
                    nuevos = []
                    for item in analisis:
                        raw = valores_actuales[item["id"]].value.strip()
                        value = to_number(raw) if raw else None
                        if value is not None and value <= 0:
                            raise ValueError
                        nuevos.append(actualizar_precio_actual(item, value))
                    mostrar(nuevos)
                    estado_error.value = ""
                except (ValueError, TypeError):
                    estado_error.value = "Ingresá precios actuales mayores a cero o dejá el campo vacío."
                page.update()

            def mostrar(items):
                rentables = [i for i in items if i["precio_actual"] is not None]
                mejor = max(rentables, key=lambda x: x["ganancia_actual"]) if rentables else max(items, key=lambda x: x["ganancia_estimada"])
                caro = max(items, key=lambda x: x["costo_total"])
                promedio = sum((i["margen_actual"] if i["margen_actual"] is not None else i["margen_neto"]) for i in items) / len(items)
                cards = ft.Row([
                    tarjeta("Más rentable", mejor["nombre"], f"{money(mejor.get('ganancia_actual', mejor['ganancia_estimada']))} · {mejor.get('margen_actual') if mejor.get('margen_actual') is not None else mejor['margen_neto']:.1f}%"),
                    tarjeta("Mayor costo de producción", caro["nombre"], money(caro["costo_total"])),
                    tarjeta("Margen promedio", f"{promedio:.1f}%", "Según precio actual ingresado; si falta, usa el sugerido"),
                ], spacing=12)

                # Barras de comparación construidas con controles Flet nativos.
                maximo = max([i["precio_recomendado"] for i in items] + [i["costo_total"] for i in items] + [i["precio_actual"] or 0 for i in items] + [1])
                barras = []
                for i in items[:12]:
                    series = [("Costo total", i["costo_total"], "#AEB8C2"),
                              ("Recomendado", i["precio_recomendado"], PIZZA_RED)]
                    if i["precio_actual"] is not None:
                        series.append(("Actual", i["precio_actual"], CHEESE_GOLD))
                    bars = ft.Column([ft.Row([ft.Text(label, width=92, size=11), ft.Container(width=max(4, 300 * val / maximo), height=15, bgcolor=color, border_radius=4, expand=False), ft.Text(money(val), size=11)]) for label, val, color in series], spacing=4)
                    barras.append(ft.Row([ft.Text(i["nombre"], width=170, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS), bars], vertical_alignment=ft.CrossAxisAlignment.CENTER))
                grafico_barras = ft.Container(ft.Column([ft.Text("Costo total vs. precio recomendado y actual", size=17, weight=ft.FontWeight.BOLD), *barras], spacing=9), bgcolor=WHITE, padding=18, border_radius=12, shadow=soft_shadow())

                # Distribución por estado representada como segmentos proporcionales.
                colores = {"Estrella": ft.Colors.GREEN_500, "Estándar": ft.Colors.AMBER_500, "Crítico": ft.Colors.RED_500}
                conteos = {name: sum(1 for i in items if i["estado"] == name) for name in colores}
                segmentos = [ft.Container(expand=count, height=24, bgcolor=colores[name], border_radius=4) for name, count in conteos.items() if count]
                leyenda = ft.Row([ft.Row([ft.Container(width=12, height=12, bgcolor=colores[name]), ft.Text(f"{name}: {conteos[name]}")], spacing=6) for name in colores], wrap=True, spacing=18)
                grafico_estados = ft.Container(ft.Column([ft.Text("Conveniencia del catálogo", size=17, weight=ft.FontWeight.BOLD), ft.Row(segmentos, spacing=3) if segmentos else ft.Text("Sin productos"), leyenda]), bgcolor=WHITE, padding=18, border_radius=12, shadow=soft_shadow())

                rows = []
                for i in items:
                    color = {"Estrella": ft.Colors.GREEN_700, "Estándar": ft.Colors.AMBER_800, "Crítico": ft.Colors.RED_700}[i["estado"]]
                    margin_value = i["margen_actual"] if i["margen_actual"] is not None else i["margen_neto"]
                    rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(i["nombre"])), ft.DataCell(ft.Text(money(i["costo_mp"]))),
                        ft.DataCell(ft.Text(money(i["costo_total"]))), ft.DataCell(ft.Text(money(i["precio_recomendado"]))),
                        ft.DataCell(ft.Text(f"{margin_value:.1f}%")),
                        ft.DataCell(ft.Container(ft.Text(i["estado"], color=ft.Colors.WHITE, size=12), bgcolor=color, padding=ft.Padding(8, 4, 8, 4), border_radius=12)),
                        ft.DataCell(valores_actuales[i["id"]]),
                    ]))
                tabla = ft.Container(ft.Column([ft.Text("Detalle por producto", size=17, weight=ft.FontWeight.BOLD), simple_table(["Producto", "Costo MP", "Costo total", "Precio recomendado", "% Margen", "Estado", "Precio actual (opcional)"], rows), ft.FilledButton("Comparar precios actuales", icon=ft.Icons.REFRESH, on_click=actualizar)]), bgcolor=WHITE, padding=18, border_radius=12, shadow=soft_shadow())
                dashboard.controls = [cards, grafico_barras, grafico_estados, tabla]

            mostrar([actualizar_precio_actual(i, None) for i in analisis])
            estado_error.value = ""
        except Exception as exc:
            estado_error.value = f"No se pudo calcular el análisis: {exc}"
            dashboard.controls = []
        page.update()

    margen.on_change = build
    build()
    return ft.Column([
        page_heading("Estrategia de precios", "Revisá costos, márgenes y precios sugeridos para el catálogo de Los Tilos."),
        ft.Container(ft.Column([margen_texto, margen, ft.Text("Precio sugerido = costo total × (1 + recargo). El margen neto se calcula sobre el precio de venta.")]), bgcolor=WHITE, padding=18, border_radius=12, shadow=soft_shadow()),
        estado_error, dashboard,
        ft.Text("Estimación de costos generales: los montos activos se distribuyen en partes iguales entre los productos activos porque el sistema no registra unidades producidas ni una base de asignación por producto. El período de cada costo también se conserva como referencia y no se normaliza.", size=11, color=ft.Colors.BLUE_GREY_600),
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=14)
