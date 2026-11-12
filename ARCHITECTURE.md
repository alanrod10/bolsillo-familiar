# Arquitectura de BolsilloFamiliar

## Stack Tecnológico
- **Framework:** Django 5.2 LTS
- **Base de Datos:** SQLite
- **Frontend:** HTML, CSS (Vanilla), sistema de grillas nativo responsivo.
- **Patrón Arquitectónico:** Monolítico, MVC (Model-View-Template en Django).

## Capa de Servicios (Reglas de Negocio)
La lógica financiera estricta no reside en las vistas, sino en la capa de servicios (`finance/services/`):
- `balances.py`: Cálculo en tiempo real de saldos omitiendo transacciones anuladas.
- `transactions.py`: Creación atómica de movimientos y reversión segura (liberación de cuotas).
- `transfers.py`: Movimientos neutros de patrimonio entre cuentas del mismo hogar.
- `budgets.py`: Consolidación de gastos contra topes mensuales.
- `obligations.py`: Prorrateo matemático exacto de deudas (ajuste de centavos en cuota final) y pagos atómicos.

## Seguridad y Aislamiento
- Cada entidad (Account, Category, Transaction, Budget, Obligation) está estrictamente vinculada a un modelo `Household` (Hogar).
- Validaciones en backend (Forms y Services) previenen la interacción entre datos de diferentes hogares.
