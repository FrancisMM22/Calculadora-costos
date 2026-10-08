import flet as ft

from components.branding import page_heading
from components.dialogs import close_dialog, confirm, show_dialog
from components.tables import action_buttons, simple_table
from services.calculadora import ingredient_cost, product_cost
from utils.helpers import (
    PRODUCT_CATEGORIES,
    compatible_units,
    money,
    to_number,
    unit_family,
)


def productos_view(page, db, refresh, open_new=False):
    search = ft.TextField(
        label="Buscar productos",
        prefix_icon=ft.Icons.SEARCH,
        width=300,
        dense=True,
    )
    host = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def rebuild(e=None):
        rows = []
        for product in db.list_products(search.value or ""):
            cost = product_cost(db.product_ingredients(product["id"]))
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(product["nombre"])),
                        ft.DataCell(ft.Text(product["categoria"] or "—")),
                        ft.DataCell(ft.Text(product["rendimiento"] or "—")),
                        ft.DataCell(
                            ft.Text(money(cost), weight=ft.FontWeight.BOLD)
                        ),
                        ft.DataCell(
                            action_buttons(
                                lambda e, p=product: form(p),
                                lambda e, p=product: remove(p),
                            )
                        ),
                    ]
                )
            )
        host.controls = (
            [
                simple_table(
                    [
                        "Producto",
                        "Categoría",
                        "Rendimiento",
                        "Costo actual",
                        "",
                    ],
                    rows,
                )
            ]
            if rows
            else [
                ft.Container(
                    ft.Text("No se encontraron productos."), padding=25
                )
            ]
        )
        page.update()

    search.on_change = rebuild

    def form(product=None):
        values = {
            key: product[key] if product else ""
            for key in ("nombre", "categoria", "descripcion", "rendimiento")
        }
        ingredients = (
            [dict(item) for item in db.product_ingredients(product["id"])]
            if product
            else []
        )
        current_category = values["categoria"] or None
        categories = PRODUCT_CATEGORIES + (
            [current_category]
            if current_category and current_category not in PRODUCT_CATEGORIES
            else []
        )
        name = ft.TextField(
            label="Nombre *", value=values["nombre"], autofocus=True
        )
        category = ft.Dropdown(
            label="Categoría *",
            value=current_category,
            options=[ft.dropdown.Option(value) for value in categories],
            width=240,
        )
        description = ft.TextField(
            label="Descripción",
            value=values["descripcion"],
            multiline=True,
            min_lines=1,
            max_lines=2,
        )
        yield_field = ft.TextField(
            label="Rendimiento",
            value=values["rendimiento"],
            hint_text="Ej.: 12 unidades",
        )
        error = ft.Text("", color=ft.Colors.RED_600)
        ingredients_host = ft.Column(spacing=4)
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar producto" if product else "Nuevo producto"),
            content=ft.Container(
                width=720,
                height=580,
                content=ft.Column(
                    [
                        name,
                        ft.Row([category, yield_field]),
                        description,
                        ft.Row(
                            [
                                ft.Text(
                                    "Receta / ingredientes",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.FilledButton(
                                    "Agregar ingrediente",
                                    icon=ft.Icons.ADD,
                                    on_click=lambda e: ingredient_form(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ingredients_host,
                        error,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
        )

        def draw_ingredients():
            rows = []
            for index, item in enumerate(ingredients):
                actions = ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.EDIT_OUTLINED,
                            tooltip="Editar ingrediente",
                            on_click=lambda e, i=index: ingredient_form(i),
                        ),
                        ft.IconButton(
                            ft.Icons.DELETE_OUTLINE,
                            tooltip="Eliminar ingrediente",
                            icon_color=ft.Colors.RED_400,
                            on_click=lambda e, i=index: ask_delete_ingredient(
                                i
                            ),
                        ),
                    ],
                    spacing=0,
                )
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item["nombre"])),
                            ft.DataCell(ft.Text(f"{item['cantidad']:g}")),
                            ft.DataCell(ft.Text(item["unidad"])),
                            ft.DataCell(
                                ft.Text(money(ingredient_cost(item)))
                            ),
                            ft.DataCell(actions),
                        ]
                    )
                )
            total = product_cost(ingredients)
            ingredients_host.controls = (
                [
                    simple_table(
                        [
                            "Materia prima",
                            "Cantidad",
                            "Unidad",
                            "Costo",
                            "Acción",
                        ],
                        rows,
                    ),
                    ft.Text(
                        f"COSTO TOTAL DE LA RECETA: {money(total)}",
                        weight=ft.FontWeight.BOLD,
                    ),
                ]
                if rows
                else [
                    ft.Text(
                        "Todavía no agregaste ingredientes.", italic=True
                    )
                ]
            )
            page.update()

        def ask_delete_ingredient(index):
            ingredient_name = ingredients[index]["nombre"]
            confirm(
                page,
                "Eliminar ingrediente",
                f"¿Querés eliminar '{ingredient_name}' de esta receta?",
                lambda: (ingredients.pop(index), draw_ingredients()),
            )

        def ingredient_form(edit_index=None):
            materials = db.list_raw_materials()

            if not materials:
                error.value = "Primero necesitás crear una materia prima."
                page.update()
                return

            original = (
                ingredients[edit_index] if edit_index is not None else None
            )
            original_material = next(
                (
                    item
                    for item in materials
                    if original
                    and str(item["id"]) == str(original["materia_prima_id"])
                ),
                None,
            )
            initial_units = (
                compatible_units(original_material["unidad_compra"])
                if original_material
                else []
            )

            selected = ft.Dropdown(
                label="Materia prima *",
                value=str(original["materia_prima_id"]) if original else None,
                options=[
                    ft.dropdown.Option(key=str(item["id"]), text=item["nombre"])
                    for item in materials
                ],
                width=300,
            )

            quantity = ft.TextField(
                label="Cantidad *",
                value=f"{original['cantidad']:g}" if original else "",
                keyboard_type=ft.KeyboardType.NUMBER,
                width=150,
            )

            unit = ft.Dropdown(
                label="Unidad *",
                value=(
                    original["unidad"]
                    if original and original.get("unidad") in initial_units
                    else initial_units[0] if initial_units else None
                ),
                options=[
                    ft.dropdown.Option(
                        key=choice,
                        text=choice,
                    )
                    for choice in initial_units
                ],
                width=180,
                disabled=False,
                hint_text=None if initial_units else "Elegí una materia prima",
            )
            unit_host = ft.Container(content=unit, width=180)
            unit_diagnostic = ft.Text(size=11, color=ft.Colors.BLUE_GREY_600)

            ingredient_error = ft.Text("", color=ft.Colors.RED_600)

            ingredient_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    "Editar ingrediente"
                    if original
                    else "Agregar ingrediente"
                ),
                content=ft.Column(
                    [
                        selected,
                        ft.Row([quantity, unit_host]),
                        unit_diagnostic,
                        ingredient_error,
                    ],
                    tight=True,
                ),
            )

            def selected_material():
                if selected.value is None:
                    return None
                # Convertimos ambos lados a string para evitar fallos si uno es int y el otro str
                val_str = str(selected.value)
                return next(
                    (item for item in materials if str(item["id"]) == val_str),
                    None,
                )

            def update_unit_diagnostic(event_status="Esperando selección"):
                material = selected_material()
                purchase_unit = (
                    material.get("unidad_compra") if material else None
                )
                option_labels = [
                    option.text or option.key
                    for option in unit.options
                ]
                in_current_host = unit_host.content is unit
                unit_diagnostic.value = (
                    f"Materia prima: {material['nombre'] if material else 'sin seleccionar'}"
                    f" | Compra: {purchase_unit or '—'}"
                    f" | Opciones: {', '.join(option_labels) or '—'}"
                    f" | Seleccionada: {unit.value or '—'}"
                    f" | Habilitado: {'sí' if not unit.disabled else 'no'}"
                    f" | Visible: {'sí' if unit.visible else 'no'}"
                    f" | Opacidad: {unit.opacity:g}"
                    f" | Ancho: {unit.width}"
                    f" | Control actual en contenedor: {'sí' if in_current_host else 'no'}"
                    f" | {event_status}"
                )

            def unit_received_focus(e):
                update_unit_diagnostic(
                    "El selector recibió foco/clic"
                    if e.control is unit
                    else "El evento llegó a un control anterior"
                )
                page.update(unit_diagnostic)

            def unit_changed(e):
                update_unit_diagnostic(
                    "La selección de unidad cambió"
                    if e.control is unit
                    else "El evento llegó a un control anterior"
                )
                page.update(unit_diagnostic)

            unit.on_focus = unit_received_focus
            unit.on_select = unit_changed
            update_unit_diagnostic()

            def set_units(e=None):
                nonlocal unit
                material = selected_material()
                unidad_compra = material.get("unidad_compra") if material else None

                if material and unidad_compra:
                    choices = compatible_units(unidad_compra)
                    selected_unit = (
                        unit.value if unit.value in choices else choices[0]
                    )
                    hint_text = None
                else:
                    choices = []
                    selected_unit = None
                    hint_text = "Elegí una materia prima"

                # Dropdown.options no se marca como modificada al reasignarla
                # en Flet 0.86.1. Reemplazar el control fuerza a Flet a enviar
                # su configuración completa al cliente, incluso en el diálogo
                # de ingrediente anidado.
                unit = ft.Dropdown(
                    label="Unidad *",
                    value=selected_unit,
                    options=[
                        ft.dropdown.Option(
                            key=choice,
                            text=choice,
                        )
                        for choice in choices
                    ],
                    width=180,
                    disabled=False,
                    hint_text=hint_text,
                )
                unit.on_focus = unit_received_focus
                unit.on_select = unit_changed
                unit_host.content = unit
                update_unit_diagnostic()
                page.update(unit_host, unit_diagnostic)

            selected.on_select = set_units

            def save_ingredient(e):
                try:
                    material = selected_material()
                    amount = to_number(quantity.value)

                    if not material or amount <= 0:
                        raise ValueError

                    if (
                        not unit.value
                        or unit_family(unit.value)
                        != unit_family(material.get("unidad_compra"))
                    ):
                        raise ValueError

                    if any(
                        item["materia_prima_id"] == material["id"]
                        and index != edit_index
                        for index, item in enumerate(ingredients)
                    ):
                        ingredient_error.value = (
                            "Esta materia prima ya está incluida en la receta."
                        )
                        page.update()
                        return

                    updated = {
                        "materia_prima_id": material["id"],
                        "nombre": material["nombre"],
                        "cantidad": amount,
                        "unidad": unit.value,
                        "costo_unitario": material.get("costo_unitario", 0),
                        "unidad_compra": material.get("unidad_compra", ""),
                    }

                    if original and original.get("id"):
                        updated["id"] = original["id"]

                    if edit_index is None:
                        ingredients.append(updated)
                    else:
                        ingredients[edit_index] = updated

                    close_dialog(page, ingredient_dialog)
                    draw_ingredients()

                except (ValueError, TypeError):
                    ingredient_error.value = (
                        "Completá materia prima, cantidad y una "
                        "unidad compatible. La cantidad debe ser "
                        "mayor a cero."
                    )
                    page.update()

            ingredient_dialog.actions = [
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: close_dialog(page, ingredient_dialog),
                ),
                ft.FilledButton(
                    "Guardar",
                    on_click=save_ingredient,
                ),
            ]

            show_dialog(page, ingredient_dialog)

        def save(e):
            if not name.value.strip():
                error.value = "El nombre del producto es obligatorio."
                page.update()
                return
            if not category.value:
                error.value = "Elegí una categoría para el producto."
                page.update()
                return
            db.save_product(
                {
                    "nombre": name.value.strip(),
                    "categoria": category.value,
                    "descripcion": description.value.strip(),
                    "rendimiento": yield_field.value.strip(),
                },
                ingredients,
                product["id"] if product else None,
            )
            close_dialog(page, dialog)
            refresh()

        dialog.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: close_dialog(page, dialog)),
            ft.FilledButton("Guardar producto", on_click=save),
        ]
        draw_ingredients()
        show_dialog(page, dialog)

    def remove(product):
        confirm(
            page,
            "Eliminar producto",
            f"¿Querés eliminar '{product['nombre']}'?",
            lambda: (db.delete_product(product["id"]), refresh()),
        )

    content = ft.Column(
        [
            ft.Row(
                [
                    ft.Container(content=page_heading("Productos / Recetas", "Creá recetas y consultá su costo actualizado."), expand=True),
                    ft.FilledButton(
                        "Nuevo producto",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: form(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            search,
            host,
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
    rebuild()
    if open_new:
        form()
    return content
