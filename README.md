# Calculadora de Costos

Aplicación de escritorio local para administrar materias primas, recetas y sus costos actualizados. Los datos se almacenan offline en SQLite (`data/costos.db`).

## Requisitos

- Python 3.10 o superior

## Ejecutar

```powershell
python -m pip install -r requirements.txt
python app.py
```

Al abrirse por primera vez, crea automáticamente la base de datos e incorpora materias primas y tres recetas de ejemplo: Pizza Muzzarella, Empanada de Carne y Empanada de Pollo.

El costo de cada receta se calcula al momento de mostrarla, usando los precios actuales de las materias primas. Por eso, actualizar un precio se refleja inmediatamente en los productos que lo usan.
