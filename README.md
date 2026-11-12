# BolsilloFamiliar

BolsilloFamiliar es una aplicación web de finanzas personales y familiares desarrollada en Django. Permite llevar un control exacto de ingresos, gastos, transferencias entre cuentas, presupuestos mensuales y cronogramas de deudas/cuotas.

## Requisitos
- Ubuntu WSL (Windows Subsystem for Linux)
- Python 3.10+
- SQLite3 (Incluido en Python)

## Instalación y Ejecución Local
1. Ingresar al entorno WSL y navegar a la carpeta del proyecto.
2. Activar el entorno virtual:
   `source ~/.venvs/bolsillo-familiar/bin/activate`
3. Instalar dependencias (si es la primera vez):
   `pip install -r requirements.txt`
4. Aplicar migraciones:
   `python manage.py migrate`
5. Levantar el servidor:
   `python manage.py runserver 127.0.0.1:8000`
6. Acceder desde el navegador en Windows a `http://127.0.0.1:8000`.

## Datos de Demostración
Para poblar la base de datos con cuentas, transacciones y presupuestos de prueba, ejecutar:
`python manage.py seed_demo`
