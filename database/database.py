from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from database.models import SCHEMA
from utils.helpers import now, unit_factor, unit_family


class Database:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    @contextmanager
    def _connect(self):
        con = sqlite3.connect(self.path, timeout=10)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")

        try:
            with con:
                yield con
        finally:
            con.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as con:
            con.executescript(SCHEMA)

            # Primera carga de materias primas si la base está vacía.
            if not con.execute(
                "SELECT 1 FROM materias_primas LIMIT 1"
            ).fetchone():
                self._seed_raw_materials(con)

            # Agrega los productos de Los Tilos que todavía no existan.
            self._seed_los_tilos_products(con)

    # =========================================================
    # DATOS INICIALES
    # =========================================================

    def _seed_raw_materials(self, con):
        raw = [
            (
                "Harina 000",
                "Harinas",
                1200,
                1,
                "kilogramos",
            ),
            (
                "Mozzarella",
                "Lácteos",
                35000,
                5,
                "kilogramos",
            ),
            (
                "Salsa de tomate",
                "Conservas",
                2800,
                1,
                "kilogramos",
            ),
            (
                "Aceite",
                "Aceites",
                4500,
                1,
                "litros",
            ),
            (
                "Sal",
                "Condimentos",
                900,
                1,
                "kilogramos",
            ),
            (
                "Carne picada",
                "Carnes",
                9500,
                1,
                "kilogramos",
            ),
            (
                "Pollo",
                "Carnes",
                7800,
                1,
                "kilogramos",
            ),
            (
                "Cebolla",
                "Verduras",
                1600,
                1,
                "kilogramos",
            ),
            (
                "Tapa de empanada",
                "Panificados",
                4200,
                12,
                "unidad",
            ),
        ]

        for name, category, price, quantity, unit in raw:
            cost = price / (quantity * unit_factor(unit))

            con.execute(
                """
                INSERT INTO materias_primas (
                    nombre,
                    categoria,
                    precio_compra,
                    cantidad_compra,
                    unidad_compra,
                    costo_unitario,
                    fecha_actualizacion,
                    activo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    name,
                    category,
                    price,
                    quantity,
                    unit,
                    cost,
                    now(),
                ),
            )

    def _seed_los_tilos_products(self, con):
        """
        Carga el catálogo actual de Los Tilos.

        Importante:
        - No se inventan cantidades de ingredientes.
        - Los productos quedan disponibles para editar desde la aplicación.
        - Si un producto ya existe, no se duplica.
        """

        products = [
            # =================================================
            # PIZZAS
            # =================================================

            (
                "Muzzarella",
                "Pizzas",
                "Salsa de tomates, muzzarella, aceitunas, oregano.",
                "1 pizza",
            ),
            (
                "Muzzarella Doble",
                "Pizzas",
                "Salsa de tomates, doble porcion de muzzarella, doble porcion de aceitunas, oregano.",
                "1 pizza",
            ),
            (
                "Napolitana",
                "Pizzas",
                "Salsa de tomates, muzzarella, tomates cherry, tomates en rodajas, aceitunas, ajo picado, oregano, queso parmesano rallado.",
                "1 pizza",
            ),
            (
                "Napolitana con Jamón",
                "Pizzas",
                "Salsa de tomates, muzzarella, jamon cocido natural, tomates en rodajas, tomates cherry aceitunas, ajo picado, oregano, queso parmesano rallado.",
                "1 pizza",
            ),
            (
                "Jamón",
                "Pizzas",
                "Salsa de tomates, muzzarella, jamón cocido natural, aceitunas, oregano.",
                "1 pizza",
            ),
            (
                "Jamón y Morrones",
                "Pizzas",
                "Salsa de tomates, muzzarella, jamón cocido natural, morrones asados en oliva, aceitunas, ajo asado, oregano.",
                "1 pizza",
            ),
            (
                "Calabresa",
                "Pizzas",
                "Salsa de tomates, muzzarella, salame calabrese en rodajas, oregano, pimienta negra molida.",
                "1 pizza",
            ),
            (
                "Tandilense",
                "Pizzas",
                "Salsa de tomates, muzzarella, salame tandilense en rodajas, aji molido, oregano.",
                "1 pizza",
            ),
            (
                "Anchoas",
                "Pizzas",
                "Salsa de tomates, anchoas en oliva, queso parmesano rallado.",
                "1 pizza",
            ),
            (
                "Fugazza",
                "Pizzas",
                "Cebolla blanca en juliana, cebolla morada en juliana, oliva, oregano.",
                "1 pizza",
            ),
            (
                "Fugazza con Muzzarella",
                "Pizzas",
                "Cebolla blanca en juliana, cebolla morada en juliana, oliva, oregano, muzzarela.",
                "1 pizza",
            ),
            (
                "Fugazzeta",
                "Pizzas",
                "Rellena con muzzarela, cebolla blanca en juliana, cebolla morada en juliana, oliva, oregano.",
                "1 pizza",
            ),
            (
                "Fugazzeta con Jamón",
                "Pizzas",
                "Rellena con jamon cocido natural y muzzarella, cebolla blanca en juliana, cebolla morada en juliana, oliva, oregano.",
                "1 pizza",
            ),
            (
                "4 Quesos",
                "Pizzas",
                "Salsa de tomates, muzzarella, provolone, queso azul, parmesano rallado, aceitunas, oregano.",
                "1 pizza",
            ),
            (
                "Provolone",
                "Pizzas",
                "Salsa de tomates, muzzarella, provolone, aceitunas negras, oliva, oregano.",
                "1 pizza",
            ),
            (
                "Roquefort",
                "Pizzas",
                "Salsa de tomates, muzzarella, queso azul, oliva.",
                "1 pizza",
            ),
            (
                "Caprese",
                "Pizzas",
                "Salsa de tomates, muzzarela, albahaca, tomates cherri, oliva.",
                "1 pizza",
            ),
            (
                "Huevo con Jamón",
                "Pizzas",
                "Salsa de tomates, muzzarella, jamon cocido natural, huevos duros picados, aceitunas.",
                "1 pizza",
            ),
            (
                "Huevo y Mayonesa",
                "Pizzas",
                "Mayonesa, huevo duro picado.",
                "1 pizza",
            ),
            (
                "Palmitos",
                "Pizzas",
                "Salsa de tomates, muzzarella, jamon cocido natural, salsa golf, palmitos, aceitunas negras, oregano, oliva.",
                "1 pizza",
            ),
            (
                "Rúcula y Bondiola",
                "Pizzas",
                "Salsa de tomates, muzzarella, bondiola de cerdo ahumada, rucula, queso parmesano rallado, aceitunas negras, oliva.",
                "1 pizza",
            ),
            (
                "Fainá x porción",
                "Pizzas",
                "Tradicional porción de fainá crocante a base de harina de garbanzos.",
                "1 porción",
            ),
            (
                "Calzone Napolitano",
                "Pizzas",
                "Relleno de jamon cocido natural, muzzarela, salsa de tomates, tomates frescos en rodajas, aceitunas, oliva, oregano.",
                "1 unidad",
            ),
            (
                "Calzone Calabrese",
                "Pizzas",
                "Relleno de salsa de tomates, muzzarela, salame calabrese en rodajas.",
                "1 unidad",
            ),
            (
                "Vienesa",
                "Pizzas",
                "Salsa de tomates, muzzarella, salchichas tipo viena, mostaza.",
                "1 pizza",
            ),
            (
                "Salchipapa",
                "Pizzas",
                "Salsa de tomate, muzzarela, salchichas tipo viena, papas fritas.",
                "1 pizza",
            ),
            (
                "Espinaca y Salsa Blanca",
                "Pizzas",
                "Salteado de espinacas, cebollas, morrones con salsa bechamel.",
                "1 pizza",
            ),
            (
                "Primavera",
                "Pizzas",
                "Salsa de tomate, muzzarella, jamon cocido natural, huevo duro picado, tomates frescos en cubos, aceitunas, queso parmesano rallado, oliva.",
                "1 pizza",
            ),
            (
                "Panceta y Cheddar",
                "Pizzas",
                "Salsa de tomate, muzzarela, panceta ahumada de cerdo, queso cheddar.",
                "1 pizza",
            ),
            (
                "Porción de Fugazzeta",
                "Pizzas",
                "Porción individual de fugazzeta simple.",
                "1 porción",
            ),
            (
                "Porción de Fugazzeta c/ Jamón",
                "Pizzas",
                "Porción individual de fugazzeta con jamón.",
                "1 porción",
            ),

            # =================================================
            # EMPANADAS
            # =================================================

            (
                "1 Docena de Empanadas",
                "Empanadas",
                "Pack de 12 empanadas a elección. Armalas combinando tus gustos preferidos.",
                "12 unidades",
            ),
            (
                "1/2 Docena de Empanadas",
                "Empanadas",
                "Pack de 6 empanadas a elección. Podés combinar los sabores que quieras.",
                "6 unidades",
            ),
            (
                "Empanada por unidad",
                "Empanadas",
                "Empanada individual a elección.",
                "1 unidad",
            ),

            # =================================================
            # COMBOS
            # =================================================

            (
                "Combo Niño",
                "Combos",
                "Incluye 1/4 kg de helado, 2 empanadas y 1 gaseosa chica a elección.",
                "1 combo",
            ),
            (
                "Combo Pareja",
                "Combos",
                "Incluye 1/2 docena de empanadas, 1/2 kg de helado y 1 gaseosa de 1,25 L a elección.",
                "1 combo",
            ),
            (
                "Combo Finde",
                "Combos",
                "Incluye 1 pizza de muzzarella, 1/2 docena de empanadas, 1/2 kg de helado y 1 jugo Placer de 1,25 L de regalo.",
                "1 combo",
            ),
            (
                "Combo de la Casa",
                "Combos",
                "Incluye 1 pizza de muzzarella, 1 pizza napolitana, 1 docena de empanadas, 1 gaseosa de 1,25 L a elección y 1 jugo Placer.",
                "1 combo",
            ),

            # =================================================
            # HELADOS
            # =================================================

            (
                "Helado 1/4 Kg",
                "Helados",
                "Pote de un cuarto kilo. Elegí hasta 3 gustos de nuestra lista artesanal.",
                "1 pote",
            ),
            (
                "Helado 1/2 Kg",
                "Helados",
                "Pote de medio kilo. Elegí hasta 3 gustos de nuestra lista artesanal.",
                "1 pote",
            ),
            (
                "Helado 1 Kg",
                "Helados",
                "Pote de un kilo ideal para compartir. Elegí hasta 4 gustos artesanales.",
                "1 pote",
            ),

            # =================================================
            # TARTAS
            # =================================================

            (
                "Tarta Verdura Grande",
                "Tartas",
                "Tarta grande 32 cm (salteado de verduras de hoja, cebollas, pimientos, huevo, parmesano).",
                "1 tarta",
            ),
            (
                "Tarta Verdura Chica",
                "Tartas",
                "Tarta chica 20 cm (salteado de verduras de hoja, cebollas, pimientos, huevo, parmesano).",
                "1 tarta",
            ),
            (
                "Tarta Pollo Grande",
                "Tartas",
                "Tarta grande 32 cm (pollo en trozos, cebollas, pimientos, huevos).",
                "1 tarta",
            ),
            (
                "Tarta Pollo Chica",
                "Tartas",
                "Tarta chica 20 cm (pollo en trozos, cebollas, pimientos, huevo).",
                "1 tarta",
            ),
            (
                "Tarta de Jamon y Queso Grande",
                "Tartas",
                "Tarta grande 32cm (jamon cocido natural, muzzarela, parmesano rallado, huevos).",
                "1 tarta",
            ),
            (
                "Tarta Jamon y Queso chica",
                "Tartas",
                "Tarta chica 20cm (jamon cocido natural, muzzarella, parmesano rallado, huevos).",
                "1 tarta",
            ),

            # =================================================
            # FOCCACCIA
            # =================================================

            (
                "Focaccia Bondiola, Rúcula y Mix de Quesos",
                "Focaccia",
                "Bondiola, rucula, mix de quesos.",
                "1 unidad",
            ),
            (
                "Focaccia Pesto, Jamón y Roquefort",
                "Focaccia",
                "Pesto, jamon, roquefort, cebollas caramelizadas.",
                "1 unidad",
            ),
            (
                "Focaccia Panceta, Ajíes, Queso Crema y Verdeo",
                "Focaccia",
                "Panceta, ajies en vinagre, queso crema y verdeo.",
                "1 unidad",
            ),

            # =================================================
            # BEBIDAS
            # =================================================

            (
                "Coca Cola 500 ml",
                "Bebidas",
                "Bebida Coca Cola de 500ml.",
                "1 unidad",
            ),
            (
                "Sprite 500 ml",
                "Bebidas",
                "Gaseosa marca Sprite de 500ml.",
                "1 unidad",
            ),
            (
                "Fanta 500 ml",
                "Bebidas",
                "Gaseosa marca Fanta de 500 ml.",
                "1 unidad",
            ),
            (
                "Coca Cola 1.5 L",
                "Bebidas",
                "Gaseosa marca Coca Cola 1.5 L.",
                "1 unidad",
            ),
            (
                "Fanta 1.5 L",
                "Bebidas",
                "Gaseosa marca Fanta 1.5 L.",
                "1 unidad",
            ),
            (
                "Sprite 1.5 L",
                "Bebidas",
                "Gaseosa marca Sprite 1.5 L.",
                "1 unidad",
            ),
            (
                "Placer 1.25L",
                "Bebidas",
                "Jugo Placer 1.25 L Sabor Naranja.",
                "1 unidad",
            ),
            (
                "Brahma 473ml",
                "Bebidas",
                "Cerveza Brahma 473ml.",
                "1 unidad",
            ),
            (
                "Brahma 710ml.",
                "Bebidas",
                "Cerveza Brahma 710ml.",
                "1 unidad",
            ),
            (
                "Quilmes 473cc.",
                "Bebidas",
                "Cerveza Quilmes 473cc.",
                "1 unidad",
            ),
            (
                "Quilmes 710cc.",
                "Bebidas",
                "Cerveza Quilmes 710cc.",
                "1 unidad",
            ),
            (
                "Heineken 473 cc.",
                "Bebidas",
                "Cerveza Heineken 473cc.",
                "1 unidad",
            ),
            (
                "Heineken 710 cc",
                "Bebidas",
                "Cerveza Heineken 710 cc.",
                "1 unidad",
            ),
        ]

        for name, category, description, yield_text in products:
            existing = con.execute(
                "SELECT id FROM productos WHERE nombre = ? LIMIT 1",
                (name,),
            ).fetchone()

            if existing:
                continue

            con.execute(
                """
                INSERT INTO productos (
                    nombre,
                    categoria,
                    descripcion,
                    rendimiento,
                    activo
                )
                VALUES (?, ?, ?, ?, 1)
                """,
                (
                    name,
                    category,
                    description,
                    yield_text,
                ),
            )

    # =========================================================
    # CONSULTAS GENERALES
    # =========================================================

    def query(
        self,
        sql: str,
        params: tuple = (),
    ) -> list[dict[str, Any]]:
        with self._connect() as con:
            return [
                dict(row)
                for row in con.execute(sql, params).fetchall()
            ]

    def one(self, sql, params=()):
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def execute(self, sql, params=()):
        with self._connect() as con:
            return con.execute(sql, params).lastrowid

    # =========================================================
    # MATERIAS PRIMAS
    # =========================================================

    def list_raw_materials(self, search=""):
        return self.query(
            """
            SELECT *
            FROM materias_primas
            WHERE activo = 1
              AND nombre LIKE ?
            ORDER BY nombre
            """,
            (f"%{search}%",),
        )

    def save_raw_material(self, v, raw_id=None):
        if v["precio_compra"] <= 0 or v["cantidad_compra"] <= 0:
            raise ValueError("El precio y la cantidad deben ser mayores a cero.")
        # Cambiar de peso a volumen (o a unidad) dejaría recetas existentes
        # con cantidades dimensionalmente incompatibles.
        if raw_id:
            current = self.one(
                "SELECT unidad_compra FROM materias_primas WHERE id=?",
                (raw_id,),
            )
            if current and unit_family(current["unidad_compra"]) != unit_family(v["unidad_compra"]):
                used = self.one(
                    "SELECT COUNT(*) total FROM producto_ingredientes WHERE materia_prima_id=?",
                    (raw_id,),
                )["total"]
                if used:
                    raise ValueError(
                        "No se puede cambiar la familia de unidad de una materia prima usada en recetas."
                    )
        cost = v["precio_compra"] / (
            v["cantidad_compra"] * unit_factor(v["unidad_compra"])
        )

        p = (
            v["nombre"],
            v["categoria"],
            v["precio_compra"],
            v["cantidad_compra"],
            v["unidad_compra"],
            cost,
            now(),
        )

        if raw_id:
            self.execute(
                """
                UPDATE materias_primas
                SET nombre=?,
                    categoria=?,
                    precio_compra=?,
                    cantidad_compra=?,
                    unidad_compra=?,
                    costo_unitario=?,
                    fecha_actualizacion=?
                WHERE id=?
                """,
                p + (raw_id,),
            )
            return raw_id

        return self.execute(
            """
            INSERT INTO materias_primas (
                nombre,
                categoria,
                precio_compra,
                cantidad_compra,
                unidad_compra,
                costo_unitario,
                fecha_actualizacion,
                activo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            """,
            p,
        )

    def delete_raw_material(self, raw_id):
        self.execute(
            "DELETE FROM materias_primas WHERE id=?",
            (raw_id,),
        )

    def raw_usage_count(self, raw_id):
        result = self.one(
            """
            SELECT COUNT(DISTINCT producto_id) total
            FROM producto_ingredientes
            WHERE materia_prima_id=?
            """,
            (raw_id,),
        )

        return result["total"]

    # =========================================================
    # PRODUCTOS
    # =========================================================

    def list_products(self, search=""):
        return self.query(
            """
            SELECT *
            FROM productos
            WHERE activo = 1
              AND nombre LIKE ?
            ORDER BY nombre
            """,
            (f"%{search}%",),
        )

    def product_ingredients(self, product_id):
        return self.query(
            """
            SELECT
                pi.id,
                pi.materia_prima_id,
                pi.cantidad,
                pi.unidad,
                mp.nombre,
                mp.costo_unitario,
                mp.unidad_compra
            FROM producto_ingredientes pi
            JOIN materias_primas mp
                ON mp.id = pi.materia_prima_id
            WHERE pi.producto_id=?
            ORDER BY pi.id
            """,
            (product_id,),
        )

    def save_product(
        self,
        v,
        ingredients,
        product_id=None,
    ):
        p = (
            v["nombre"],
            v["categoria"],
            v["descripcion"],
            v["rendimiento"],
        )

        with self._connect() as con:
            if product_id:
                con.execute(
                    """
                    UPDATE productos
                    SET nombre=?,
                        categoria=?,
                        descripcion=?,
                        rendimiento=?
                    WHERE id=?
                    """,
                    p + (product_id,),
                )

                existing_ids = {
                    row["id"]
                    for row in con.execute(
                        """
                        SELECT id
                        FROM producto_ingredientes
                        WHERE producto_id=?
                        """,
                        (product_id,),
                    )
                }

            else:
                product_id = con.execute(
                    """
                    INSERT INTO productos (
                        nombre,
                        categoria,
                        descripcion,
                        rendimiento,
                        activo
                    )
                    VALUES (?, ?, ?, ?, 1)
                    """,
                    p,
                ).lastrowid

                existing_ids = set()

            retained_ids = []

            for ingredient in ingredients:
                ingredient_id = ingredient.get("id")

                if ingredient_id in existing_ids:
                    con.execute(
                        """
                        UPDATE producto_ingredientes
                        SET materia_prima_id=?,
                            cantidad=?,
                            unidad=?
                        WHERE id=?
                          AND producto_id=?
                        """,
                        (
                            ingredient["materia_prima_id"],
                            ingredient["cantidad"],
                            ingredient["unidad"],
                            ingredient_id,
                            product_id,
                        ),
                    )

                    retained_ids.append(ingredient_id)

                else:
                    con.execute(
                        """
                        INSERT INTO producto_ingredientes (
                            producto_id,
                            materia_prima_id,
                            cantidad,
                            unidad
                        )
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            product_id,
                            ingredient["materia_prima_id"],
                            ingredient["cantidad"],
                            ingredient["unidad"],
                        ),
                    )

            if existing_ids:
                if retained_ids:
                    placeholders = ",".join(
                        "?" for _ in retained_ids
                    )

                    con.execute(
                        f"""
                        DELETE FROM producto_ingredientes
                        WHERE producto_id=?
                          AND id NOT IN ({placeholders})
                        """,
                        (
                            product_id,
                            *retained_ids,
                        ),
                    )
                else:
                    con.execute(
                        """
                        DELETE FROM producto_ingredientes
                        WHERE producto_id=?
                        """,
                        (product_id,),
                    )

        return product_id

    def delete_product(self, product_id):
        self.execute(
            "DELETE FROM productos WHERE id=?",
            (product_id,),
        )

    # =========================================================
    # COSTOS GENERALES
    # =========================================================

    def list_general_costs(
        self,
        search="",
        include_inactive=True,
    ):
        active_clause = "" if include_inactive else "AND activo=1"

        return self.query(
            f"""
            SELECT *
            FROM costos_generales
            WHERE nombre LIKE ?
               OR categoria LIKE ?
            {active_clause}
            ORDER BY activo DESC, nombre
            """,
            (
                f"%{search}%",
                f"%{search}%",
            ),
        )

    def save_general_cost(self, values, cost_id=None):
        params = (
            values["nombre"],
            values["categoria"],
            values["monto"],
            values["periodo"],
            now(),
        )

        if cost_id:
            self.execute(
                """
                UPDATE costos_generales
                SET nombre=?,
                    categoria=?,
                    monto=?,
                    periodo=?,
                    fecha_actualizacion=?
                WHERE id=?
                """,
                params + (cost_id,),
            )

            return cost_id

        return self.execute(
            """
            INSERT INTO costos_generales (
                nombre,
                categoria,
                monto,
                periodo,
                fecha_actualizacion,
                activo
            )
            VALUES (?, ?, ?, ?, ?, 1)
            """,
            params,
        )

    def set_general_cost_active(
        self,
        cost_id,
        active,
    ):
        self.execute(
            """
            UPDATE costos_generales
            SET activo=?
            WHERE id=?
            """,
            (
                1 if active else 0,
                cost_id,
            ),
        )

    def delete_general_cost(self, cost_id):
        self.execute(
            "DELETE FROM costos_generales WHERE id=?",
            (cost_id,),
        )
