# Calculadora de Costos

Aplicación de escritorio local para administrar materias primas, recetas y sus costos actualizados. Los datos se almacenan offline en SQLite (`data/costos.db`).

## Requisitos

- Python 3.10 o superior

## Ejecutar

```powershell
python -m pip install -r requirements.txt
python app.py
```

Al abrirse por primera vez, crea automáticamente la base de datos, incorpora materias primas de ejemplo y agrega el catálogo de productos de Los Tilos sin cantidades de receta. Los productos y materias primas ya existentes se conservan; los productos del catálogo se agregan solo si todavía no existen.

El costo de cada receta se calcula al momento de mostrarla, usando los precios actuales de las materias primas. Por eso, actualizar un precio se refleja inmediatamente en los productos que lo usan.
