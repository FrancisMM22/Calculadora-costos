import flet as ft

from components.branding import page_heading
from components.dialogs import close_dialog, confirm, show_dialog
from components.tables import action_buttons, simple_table
from utils.helpers import (
    RAW_MATERIAL_CATEGORIES,
    UNITS,
    base_unit,
    money,
    to_number,
    unit_factor,
)


def materias_primas_view(page, db, refresh, open_new=False):

    search = ft.TextField(
        label="Buscar por nombre",
        prefix_icon=ft.Icons.SEARCH,
        width=300,
        dense=True,
    )

    table_host = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    def rebuild(e=None):
        rows = []

        for item in db.list_raw_materials(search.value or ""):
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(item["nombre"])
                        ),

                        ft.DataCell(
                            ft.Text(item["categoria"] or "—")
                        ),

                        ft.DataCell(
                            ft.Text(
                                f"{money(item['precio_compra'])} / "
                                f"{item['cantidad_compra']:g} "
                                f"{item['unidad_compra']}"
                            )
                        ),

                        ft.DataCell(
                            ft.Text(
                                f"{money(item['costo_unitario'])} / "
                                f"{base_unit(item['unidad_compra'])}"
                            )
                        ),

                        ft.DataCell(
                            action_buttons(
                                lambda e, x=item: form(x),
                                lambda e, x=item: remove(x),
                            )
                        ),
                    ]
                )
            )

        table_host.controls = (
            [
                simple_table(
                    [
                        "Nombre",
                        "Categoría",
                        "Compra",
                        "Costo unitario",
                        "",
                    ],
                    rows,
                )
            ]
            if rows
            else [
                ft.Container(
                    ft.Text("No se encontraron materias primas."),
                    padding=25,
                )
            ]
        )

        page.update()

    search.on_change = rebuild

    def form(item=None):

        name = ft.TextField(
            label="Nombre *",
            value=item["nombre"] if item else "",
            autofocus=True,
        )

        current_category = item["categoria"] if item else None

        # Mantiene categorías antiguas que puedan existir
        # en la base de datos.
        categories = RAW_MATERIAL_CATEGORIES + (
            [current_category]
            if current_category
            and current_category not in RAW_MATERIAL_CATEGORIES
            else []
        )

        category = ft.Dropdown(
            label="Categoría *",
            value=current_category,
            options=[
                ft.dropdown.Option(value)
                for value in categories
            ],
            width=240,
        )

        price = ft.TextField(
            label="Precio de compra *",
            value=str(item["precio_compra"]) if item else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        quantity = ft.TextField(
            label="Cantidad comprada *",
            value=str(item["cantidad_compra"]) if item else "",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        unit = ft.Dropdown(
            label="Unidad de compra *",
            value=item["unidad_compra"]
            if item
            else "kilogramos",
            options=[
                ft.dropdown.Option(u)
                for u in UNITS
            ],
        )

        error = ft.Text(
            "",
            color=ft.Colors.RED_600,
        )

        calculation = ft.Text(
            "Completá el precio y la cantidad para ver el costo.",
            color=ft.Colors.BLUE_GREY_700,
        )

        unit_labels = {
            "gramos": "g",
            "kilogramos": "kg",
            "mililitros": "ml",
            "litros": "l",
            "unidad": "unidad",
        }

        def update_calculation(e=None):

            try:
                purchase_price = to_number(price.value)
                purchased_quantity = to_number(quantity.value)

                if (
                    purchase_price <= 0
                    or purchased_quantity <= 0
                ):
                    raise ValueError

                selected_unit = unit.value

                if not selected_unit:
                    raise ValueError

                unit_label = unit_labels[selected_unit]

                unit_cost = purchase_price / (
                    purchased_quantity
                    * unit_factor(selected_unit)
                )

                calculation.value = (
                    f"Compraste "
                    f"{purchased_quantity:g} "
                    f"{unit_label} "
                    f"por "
                    f"{money(purchase_price)}\n"
                    f"Costo: "
                    f"{money(unit_cost)} "
                    f"por "
                    f"{base_unit(selected_unit)}"
                )

            except (
                ValueError,
                TypeError,
                KeyError,
            ):
                calculation.value = (
                    "Completá el precio y la cantidad "
                    "con valores mayores a cero "
                    "para ver el costo."
                )

            page.update()

        price.on_change = update_calculation
        quantity.on_change = update_calculation
        unit.on_change = update_calculation

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Editar materia prima"
                if item
                else "Nueva materia prima"
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        name,
                        category,
                        price,

                        ft.Row(
                            [
                                quantity,
                                unit,
                            ]
                        ),

                        ft.Container(
                            content=calculation,
                            bgcolor=ft.Colors.BLUE_50,
                            padding=12,
                            border_radius=ft.BorderRadius.all(8),
                        ),

                        error,
                    ],
                    tight=True,
                    width=460,
                ),
                width=480,
            ),
        )

        def save(e):

            try:
                clean_name = name.value.strip()

                if not clean_name:
                    raise ValueError(
                        "El nombre es obligatorio."
                    )

                if not category.value:
                    raise ValueError(
                        "La categoría es obligatoria."
                    )

                if not unit.value:
                    raise ValueError(
                        "La unidad es obligatoria."
                    )

                purchase_price = to_number(price.value)
                purchased_quantity = to_number(
                    quantity.value
                )

                if purchase_price <= 0:
                    raise ValueError(
                        "El precio debe ser mayor a cero."
                    )

                if purchased_quantity <= 0:
                    raise ValueError(
                        "La cantidad debe ser mayor a cero."
                    )

                db.save_raw_material(
                    {
                        "nombre": clean_name,
                        "categoria": category.value,
                        "precio_compra": purchase_price,
                        "cantidad_compra": purchased_quantity,
                        "unidad_compra": unit.value,
                    },
                    item["id"] if item else None,
                )

                close_dialog(page, dialog)
                refresh()

            except (ValueError, TypeError) as exc:
                error.value = str(exc) or (
                    "Completá nombre, categoría, "
                    "precio, cantidad y unidad "
                    "con valores válidos."
                )

                page.update()

        dialog.actions = [
            ft.TextButton(
                "Cancelar",
                on_click=lambda e: close_dialog(
                    page,
                    dialog,
                ),
            ),

            ft.FilledButton(
                "Guardar",
                on_click=save,
            ),
        ]

        update_calculation()
        show_dialog(page, dialog)

    def remove(item):

        used = db.raw_usage_count(item["id"])

        if used:
            msg = (
                f"Esta materia prima está siendo "
                f"utilizada en {used} producto(s).\n\n"
                f"Si la eliminás, esos ingredientes "
                f"también se eliminarán.\n\n"
                f"¿Querés continuar?"
            )
        else:
            msg = (
                f"¿Querés eliminar "
                f"'{item['nombre']}'?"
            )

        confirm(
            page,
            "Eliminar materia prima",
            msg,
            lambda: (
                db.delete_raw_material(item["id"]),
                refresh(),
            ),
        )

    content = ft.Column(
        [
            ft.Row(
                [
                    ft.Container(content=page_heading("Materias primas", "Administrá los ingredientes e insumos que comprás para elaborar tus productos."), expand=True),

                    ft.FilledButton(
                        "Nueva materia prima",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: form(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),

            search,
            table_host,
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    rebuild()

    if open_new:
        form()

    return content
