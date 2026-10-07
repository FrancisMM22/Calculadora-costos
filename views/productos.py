import flet as ft

from components.dialogs import close_dialog, confirm, show_dialog
from components.tables import action_buttons, simple_table
from services.calculadora import ingredient_cost, product_cost
from utils.helpers import (
    PRODUCT_CATEGORIES,
    UNIT_LABELS,
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
                value=original.get("unidad") if original else None,
                options=[],
                width=180,
                disabled=True,
                hint_text="Elegí una materia prima",
            )

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
                        ft.Row([quantity, unit]),
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

            def set_units(e=None):
                material = selected_material()
                # Verifica que exista el material y la clave unidad_compra
                unidad_compra = material.get("unidad_compra") if material else None

                if material and unidad_compra:
                    choices = compatible_units(unidad_compra)

                    unit.options = [
                        ft.dropdown.Option(
                            key=choice,
                            text=UNIT_LABELS.get(choice, choice),
                        )
                        for choice in choices
                    ]

                    unit.disabled = False

                    if unit.value not in choices:
                        unit.value = choices[0] if choices else None

                    unit.hint_text = None
                else:
                    unit.options = []
                    unit.value = None
                    unit.disabled = True
                    unit.hint_text = "Elegí una materia prima"

                page.update()

            selected.on_change = set_units

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
            # Inicializa las opciones cuando el dropdown ya está montado.
            # Antes de abrir el diálogo page.update() no podía enviar de forma
            # fiable el cambio de disabled/options al cliente.
            set_units()

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
                    ft.Column(
                        [
                            ft.Text(
                                "Productos", size=28, weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(
                                "Creá recetas y consultá su costo"
                                " actualizado."
                            ),
                        ],
                        expand=True,
                    ),
                    ft.FilledButton(
                        "Nuevo producto",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: form(),
                    ),
                ]
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
