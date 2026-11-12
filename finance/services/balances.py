from decimal import Decimal
from django.db.models import Sum
from finance.models import Account, FinancialTransaction, Transfer

def get_account_balance(account):
    """
    Calcula el saldo real de una cuenta:
    Saldo inicial + Ingresos - Gastos + Transferencias Entrantes - Transferencias Salientes.
    Omite las transacciones anuladas.
    """
    # Sumar ingresos
    incomes = FinancialTransaction.objects.filter(
        account=account, 
        category__type='ingreso', 
        is_voided=False
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Sumar gastos
    expenses = FinancialTransaction.objects.filter(
        account=account, 
        category__type='gasto', 
        is_voided=False
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Transferencias recibidas
    transfers_in = Transfer.objects.filter(
        destination_account=account
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Transferencias enviadas
    transfers_out = Transfer.objects.filter(
        origin_account=account
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    return account.initial_balance + incomes - expenses + transfers_in - transfers_out

def get_household_total_balance(household):
    """
    Suma el saldo de todas las cuentas activas del hogar.
    """
    accounts = Account.objects.filter(household=household, is_active=True)
    return sum((get_account_balance(acc) for acc in accounts), Decimal('0.00'))
