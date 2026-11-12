import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from finance.services.balances import get_household_total_balance
from finance.models import FinancialTransaction

from django.contrib.auth import logout

@login_required
def dashboard(request):
    household = request.user.household
    total_balance = get_household_total_balance(household)
    
    today = datetime.date.today()
    
    # Ingresos y Gastos del mes actual
    incomes_month = FinancialTransaction.objects.filter(
        household=household, category__type='ingreso', is_voided=False,
        date__year=today.year, date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    expenses_month = FinancialTransaction.objects.filter(
        household=household, category__type='gasto', is_voided=False,
        date__year=today.year, date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Últimos 5 movimientos (incluyendo transferencias o pagos)
    recent_txs = FinancialTransaction.objects.filter(household=household).order_by('-date', '-id')[:5]
    
    context = {
        'household': household,
        'total_balance': total_balance,
        'incomes_month': incomes_month,
        'expenses_month': expenses_month,
        'recent_txs': recent_txs,
    }
    return render(request, 'dashboard.html', context)

def user_logout(request):
    logout(request)
    return redirect('login')

