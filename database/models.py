"""SQL schema for the local SQLite database."""

SCHEMA = """
CREATE TABLE IF NOT EXISTS materias_primas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT,
    precio_compra REAL NOT NULL CHECK(precio_compra > 0),
    cantidad_compra REAL NOT NULL CHECK(cantidad_compra > 0),
    unidad_compra TEXT NOT NULL,
    costo_unitario REAL NOT NULL,
    fecha_actualizacion TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT,
    descripcion TEXT,
    rendimiento TEXT,
    activo INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS producto_ingredientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id INTEGER NOT NULL,
    materia_prima_id INTEGER NOT NULL,
    cantidad REAL NOT NULL CHECK(cantidad > 0),
    unidad TEXT NOT NULL,
    FOREIGN KEY(producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    FOREIGN KEY(materia_prima_id) REFERENCES materias_primas(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS costos_generales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL CHECK(length(trim(nombre)) > 0),
    categoria TEXT NOT NULL CHECK(length(trim(categoria)) > 0),
    monto REAL NOT NULL CHECK(monto > 0),
    periodo TEXT NOT NULL CHECK(length(trim(periodo)) > 0),
    fecha_actualizacion TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK(activo IN (0, 1))
);
"""
