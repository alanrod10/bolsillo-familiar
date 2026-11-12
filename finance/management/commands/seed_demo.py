import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Household
from finance.models import Account, Category, Budget
from finance.services.transactions import create_transaction
from finance.services.transfers import create_transfer
from finance.services.obligations import create_obligation_with_installments, pay_installment

class Command(BaseCommand):
    help = 'Genera datos financieros ficticios y coherentes para demostración.'

    def handle(self, *args, **kwargs):
        try:
            user = User.objects.get(username='alan')
            household = user.household
            alan = household.members.get(name='Alan')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: Debes ejecutar primero la creación del usuario inicial. Detalle: {e}"))
            return

        today = datetime.date.today()
        month = today.month
        year = today.year

        self.stdout.write("Generando Cuentas...")
        acc_efectivo, _ = Account.objects.get_or_create(household=household, name='[DEMO] Efectivo Caja', type='efectivo', defaults={'initial_balance': Decimal('25000.00')})
        acc_banco, _ = Account.objects.get_or_create(household=household, name='[DEMO] Banco Macro', type='banco', defaults={'initial_balance': Decimal('150000.00')})
        acc_mp, _ = Account.objects.get_or_create(household=household, name='[DEMO] Mercado Pago', type='billetera', defaults={'initial_balance': Decimal('85000.00')})

        self.stdout.write("Generando Categorías...")
        cat_sueldo, _ = Category.objects.get_or_create(household=household, name='[DEMO] Sueldo', type='ingreso')
        cat_ventas, _ = Category.objects.get_or_create(household=household, name='[DEMO] Ventas Tienda', type='ingreso')
        cat_alimentos, _ = Category.objects.get_or_create(household=household, name='[DEMO] Alimentación', type='gasto')
        cat_servicios, _ = Category.objects.get_or_create(household=household, name='[DEMO] Servicios', type='gasto')
        cat_deudas, _ = Category.objects.get_or_create(household=household, name='[DEMO] Deudas', type='gasto')

        self.stdout.write("Generando Presupuestos...")
        Budget.objects.get_or_create(household=household, category=cat_alimentos, month=month, year=year, defaults={'limit': Decimal('250000.00')})
        Budget.objects.get_or_create(household=household, category=cat_servicios, month=month, year=year, defaults={'limit': Decimal('150000.00')})

        self.stdout.write("Procesando Ingresos...")
        create_transaction(household, '[DEMO] Sueldo Administrativo', Decimal('850000.00'), today.replace(day=5), acc_banco, cat_sueldo, alan, 'Ingreso mensual')
        create_transaction(household, '[DEMO] Recaudación Kiosco', Decimal('320000.00'), today, acc_mp, cat_ventas, alan, 'Cierre semanal')

        self.stdout.write("Procesando Gastos...")
        create_transaction(household, '[DEMO] Compra Supermercado', Decimal('95000.00'), today.replace(day=8), acc_banco, cat_alimentos, alan)
        create_transaction(household, '[DEMO] Luz y Agua', Decimal('42500.00'), today.replace(day=12), acc_mp, cat_servicios, alan)

        self.stdout.write("Ejecutando Transferencias...")
        create_transfer(household, acc_banco, acc_mp, Decimal('100000.00'), today.replace(day=10), '[DEMO] Fondeo billetera para pagos')

        self.stdout.write("Creando Obligaciones y Cuotas...")
        # Generar una deuda de 600.000 en 6 cuotas exactas
        obl = create_obligation_with_installments(
            household=household, 
            concept='[DEMO] Heladera Inelro Exhibidora', 
            creditor='Frávega', 
            total_amount=Decimal('600000.00'), 
            installments_count=6, 
            category=cat_deudas, 
            first_due_date=today.replace(day=15)
        )

        self.stdout.write("Pagando la primera cuota...")
        first_installment = obl.installments.order_by('number').first()
        if not first_installment.is_paid:
            pay_installment(first_installment.id, acc_mp, today.replace(day=15), alan)

        self.stdout.write(self.style.SUCCESS("ÉXITO: Base de datos poblada con datos demostrativos exactos."))
