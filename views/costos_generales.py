import flet as ft

from components.dialogs import close_dialog, confirm, show_dialog
from components.tables import simple_table
from utils.helpers import money, to_number

CATEGORIES = ["Servicios", "Personal", "Gastos fijos", "Mantenimiento", "Impuestos", "Otros"]


def costos_generales_view(page, db, refresh, open_new=False):
    search = ft.TextField(label="Buscar costos", prefix_icon=ft.Icons.SEARCH, width=300, dense=True)
    host = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def rebuild(e=None):
        costs = db.list_general_costs(search.value or "")
        active = [cost for cost in costs if cost["activo"]]
        period_totals = {}
        for cost in active:
            period_totals[cost["periodo"]] = period_totals.get(cost["periodo"], 0) + cost["monto"]
        summaries = [ft.Text(f"{periodo}: {money(amount)}", weight=ft.FontWeight.W_600) for periodo, amount in sorted(period_totals.items())]
        summary = ft.Container(
            content=ft.Column([
                ft.Text(f"Costos activos: {len(active)}", weight=ft.FontWeight.BOLD),
                ft.Text("Totales por período (no se combinan períodos diferentes):", color=ft.Colors.BLUE_GREY_700),
                ft.Row(summaries, wrap=True) if summaries else ft.Text("Todavía no hay costos activos."),
            ], spacing=8), bgcolor=ft.Colors.WHITE, padding=16, border_radius=10,
        )
        rows = []
        for item in costs:
            is_active = bool(item["activo"])
            toggle = ft.IconButton(
                ft.Icons.PAUSE_CIRCLE_OUTLINE if is_active else ft.Icons.REPLAY,
                tooltip="Desactivar" if is_active else "Reactivar",
                icon_color=ft.Colors.BLUE_GREY_500,
                on_click=lambda e, cost=item: set_active(cost),
            )
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(item["nombre"], color=None if is_active else ft.Colors.BLUE_GREY_400)),
                ft.DataCell(ft.Text(item["categoria"])),
                ft.DataCell(ft.Text(money(item["monto"]))),
                ft.DataCell(ft.Text(item["periodo"])),
                ft.DataCell(ft.Text(item["fecha_actualizacion"])),
                ft.DataCell(ft.Text("Activo" if is_active else "Inactivo")),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT_OUTLINED, tooltip="Editar", disabled=not is_active, on_click=lambda e, cost=item: form(cost)),
                    toggle,
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, tooltip="Eliminar", icon_color=ft.Colors.RED_400, on_click=lambda e, cost=item: remove(cost)),
                ], spacing=0)),
            ]))
        table = simple_table(["Nombre", "Categoría", "Monto", "Período / referencia", "Actualizado", "Estado", ""], rows)
        host.controls = [summary, table] if rows else [summary, ft.Container(ft.Text("No se encontraron costos generales."), padding=25)]
        page.update()

    search.on_change = rebuild

    def set_active(item):
        db.set_general_cost_active(item["id"], not bool(item["activo"]))
        rebuild()

    def remove(item):
        confirm(
            page,
            "Eliminar costo general",
            f"¿Querés eliminar '{item['nombre']}'?",
            lambda: (db.delete_general_cost(item["id"]), rebuild()),
        )

    def form(item=None):
        current = item["categoria"] if item else None
        categories = CATEGORIES + ([current] if current and current not in CATEGORIES else [])
        name = ft.TextField(label="Nombre *", value=item["nombre"] if item else "", autofocus=True)
        category = ft.Dropdown(label="Categoría *", value=current, options=[ft.dropdown.Option(value) for value in categories])
        amount = ft.TextField(label="Monto *", value=str(item["monto"]) if item else "", keyboard_type=ft.KeyboardType.NUMBER)
        period = ft.TextField(label="Período o referencia *", value=item["periodo"] if item else "Mensual", hint_text="Ej.: Mensual, Marzo 2026")
        updated = ft.Text(f"Última actualización: {item['fecha_actualizacion']}" if item else "La fecha se registra al guardar.", color=ft.Colors.BLUE_GREY_600)
        error = ft.Text("", color=ft.Colors.RED_600)
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar costo general" if item else "Nuevo costo general"),
            content=ft.Container(width=440, content=ft.Column([name, category, amount, period, updated, error], tight=True, spacing=12)),
        )

        def save(e):
            try:
                clean_name, clean_period = name.value.strip(), period.value.strip()
                if not clean_name:
                    raise ValueError("Ingresá un nombre.")
                if not category.value:
                    raise ValueError("Elegí una categoría.")
                if not clean_period:
                    raise ValueError("Ingresá un período o referencia.")
                value = to_number(amount.value)
                if value <= 0:
                    raise ValueError("El monto debe ser mayor a cero.")
                db.save_general_cost({"nombre": clean_name, "categoria": category.value, "monto": value, "periodo": clean_period}, item["id"] if item else None)
                close_dialog(page, dialog)
                refresh()
            except (ValueError, TypeError):
                error.value = "Completá nombre, categoría, monto y período con valores válidos; el monto debe ser mayor a cero."
                page.update()

        dialog.actions = [ft.TextButton("Cancelar", on_click=lambda e: close_dialog(page, dialog)), ft.FilledButton("Guardar", on_click=save)]
        show_dialog(page, dialog)

    content = ft.Column([
        ft.Row([ft.Column([ft.Text("Costos generales", size=28, weight=ft.FontWeight.BOLD), ft.Text("Registrá gastos del negocio sin asignarlos todavía a productos.")], expand=True), ft.FilledButton("Nuevo costo", icon=ft.Icons.ADD, on_click=lambda e: form())]),
        search,
        host,
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=14)
    rebuild()
    if open_new:
        form()
    return content
