from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from database.models import SCHEMA
from utils.helpers import now, unit_factor


class Database:
    def __init__(self, path: str | Path): self.path = Path(path)

    @contextmanager
    def _connect(self):
        con = sqlite3.connect(self.path)
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
            if not con.execute("SELECT 1 FROM materias_primas LIMIT 1").fetchone(): self._seed(con)

    def _seed(self, con):
        raw = [("Harina 000","Harinas",1200,1,"kilogramos"),("Mozzarella","Lácteos",35000,5,"kilogramos"),("Salsa de tomate","Conservas",2800,1,"kilogramos"),("Aceite","Aceites",4500,1,"litros"),("Sal","Condimentos",900,1,"kilogramos"),("Carne picada","Carnes",9500,1,"kilogramos"),("Pollo","Carnes",7800,1,"kilogramos"),("Cebolla","Verduras",1600,1,"kilogramos"),("Tapa de empanada","Panificados",4200,12,"unidad")]
        ids = {}
        for name, category, price, quantity, unit in raw:
            cur = con.execute("INSERT INTO materias_primas (nombre,categoria,precio_compra,cantidad_compra,unidad_compra,costo_unitario,fecha_actualizacion,activo) VALUES (?,?,?,?,?,?,?,1)", (name,category,price,quantity,unit,price/(quantity*unit_factor(unit)),now()))
            ids[name] = cur.lastrowid
        recipes = [
            ("Pizza Muzzarella","Pizzas","Pizza clásica de mozzarella","1 pizza",[("Harina 000",250,"gramos"),("Mozzarella",250,"gramos"),("Salsa de tomate",100,"gramos"),("Aceite",10,"mililitros"),("Sal",5,"gramos")]),
            ("Empanada de Carne","Empanadas","Relleno de carne","12 empanadas",[("Carne picada",500,"gramos"),("Cebolla",200,"gramos"),("Tapa de empanada",12,"unidad"),("Aceite",15,"mililitros"),("Sal",8,"gramos")]),
            ("Empanada de Pollo","Empanadas","Relleno de pollo","12 empanadas",[("Pollo",500,"gramos"),("Cebolla",200,"gramos"),("Tapa de empanada",12,"unidad"),("Aceite",15,"mililitros"),("Sal",8,"gramos")])]
        for name, category, description, yield_text, ingredients in recipes:
            pid = con.execute("INSERT INTO productos (nombre,categoria,descripcion,rendimiento,activo) VALUES (?,?,?,?,1)", (name,category,description,yield_text)).lastrowid
            con.executemany("INSERT INTO producto_ingredientes (producto_id,materia_prima_id,cantidad,unidad) VALUES (?,?,?,?)", [(pid,ids[n],q,u) for n,q,u in ingredients])

    def query(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        with self._connect() as con: return [dict(row) for row in con.execute(sql, params).fetchall()]
    def one(self, sql, params=()):
        rows = self.query(sql, params); return rows[0] if rows else None
    def execute(self, sql, params=()):
        with self._connect() as con: return con.execute(sql, params).lastrowid
    def list_raw_materials(self, search=""):
        return self.query("SELECT * FROM materias_primas WHERE activo=1 AND nombre LIKE ? ORDER BY nombre", (f"%{search}%",))
    def save_raw_material(self, v, raw_id=None):
        cost = v["precio_compra"] / (v["cantidad_compra"] * unit_factor(v["unidad_compra"]))
        p = (v["nombre"],v["categoria"],v["precio_compra"],v["cantidad_compra"],v["unidad_compra"],cost,now())
        if raw_id:
            self.execute("UPDATE materias_primas SET nombre=?,categoria=?,precio_compra=?,cantidad_compra=?,unidad_compra=?,costo_unitario=?,fecha_actualizacion=? WHERE id=?", p+(raw_id,)); return raw_id
        return self.execute("INSERT INTO materias_primas (nombre,categoria,precio_compra,cantidad_compra,unidad_compra,costo_unitario,fecha_actualizacion,activo) VALUES (?,?,?,?,?,?,?,1)", p)
    def delete_raw_material(self, raw_id): self.execute("DELETE FROM materias_primas WHERE id=?", (raw_id,))
    def raw_usage_count(self, raw_id): return self.one("SELECT COUNT(DISTINCT producto_id) total FROM producto_ingredientes WHERE materia_prima_id=?", (raw_id,))["total"]
    def list_products(self, search=""):
        return self.query("SELECT * FROM productos WHERE activo=1 AND nombre LIKE ? ORDER BY nombre", (f"%{search}%",))
    def product_ingredients(self, product_id):
        return self.query("SELECT pi.id,pi.materia_prima_id,pi.cantidad,pi.unidad,mp.nombre,mp.costo_unitario,mp.unidad_compra FROM producto_ingredientes pi JOIN materias_primas mp ON mp.id=pi.materia_prima_id WHERE pi.producto_id=? ORDER BY pi.id", (product_id,))
    def save_product(self, v, ingredients, product_id=None):
        p=(v["nombre"],v["categoria"],v["descripcion"],v["rendimiento"])
        with self._connect() as con:
            if product_id:
                con.execute("UPDATE productos SET nombre=?,categoria=?,descripcion=?,rendimiento=? WHERE id=?",p+(product_id,))
                existing_ids={row["id"] for row in con.execute("SELECT id FROM producto_ingredientes WHERE producto_id=?",(product_id,))}
            else:
                product_id=con.execute("INSERT INTO productos (nombre,categoria,descripcion,rendimiento,activo) VALUES (?,?,?,?,1)",p).lastrowid
                existing_ids=set()
            retained_ids=[]
            for ingredient in ingredients:
                ingredient_id=ingredient.get("id")
                if ingredient_id in existing_ids:
                    con.execute("UPDATE producto_ingredientes SET materia_prima_id=?,cantidad=?,unidad=? WHERE id=? AND producto_id=?",(ingredient["materia_prima_id"],ingredient["cantidad"],ingredient["unidad"],ingredient_id,product_id))
                    retained_ids.append(ingredient_id)
                else:
                    con.execute("INSERT INTO producto_ingredientes (producto_id,materia_prima_id,cantidad,unidad) VALUES (?,?,?,?)",(product_id,ingredient["materia_prima_id"],ingredient["cantidad"],ingredient["unidad"]))
            if existing_ids:
                if retained_ids:
                    placeholders=",".join("?" for _ in retained_ids)
                    con.execute(f"DELETE FROM producto_ingredientes WHERE producto_id=? AND id NOT IN ({placeholders})",(product_id,*retained_ids))
                else:
                    con.execute("DELETE FROM producto_ingredientes WHERE producto_id=?",(product_id,))
        return product_id
    def delete_product(self, product_id): self.execute("DELETE FROM productos WHERE id=?",(product_id,))

    def list_general_costs(self, search="", include_inactive=True):
        active_clause = "" if include_inactive else "AND activo=1"
        return self.query(f"SELECT * FROM costos_generales WHERE nombre LIKE ? OR categoria LIKE ? {active_clause} ORDER BY activo DESC, nombre", (f"%{search}%", f"%{search}%"))

    def save_general_cost(self, values, cost_id=None):
        params = (values["nombre"], values["categoria"], values["monto"], values["periodo"], now())
        if cost_id:
            self.execute("UPDATE costos_generales SET nombre=?,categoria=?,monto=?,periodo=?,fecha_actualizacion=? WHERE id=?", params + (cost_id,))
            return cost_id
        return self.execute("INSERT INTO costos_generales (nombre,categoria,monto,periodo,fecha_actualizacion,activo) VALUES (?,?,?,?,?,1)", params)

    def set_general_cost_active(self, cost_id, active):
        self.execute("UPDATE costos_generales SET activo=? WHERE id=?", (1 if active else 0, cost_id))

    def delete_general_cost(self, cost_id):
        self.execute("DELETE FROM costos_generales WHERE id=?", (cost_id,))
