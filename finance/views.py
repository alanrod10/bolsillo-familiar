import csv
import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from finance.models import Transfer, Account, Obligation, ObligationInstallment, FinancialTransaction
from finance.forms import TransactionForm, TransferForm, ObligationForm, InstallmentPayForm
from finance.services.transactions import create_transaction
from finance.services.transfers import create_transfer
from finance.services.balances import get_account_balance
from finance.services.obligations import create_obligation_with_installments, pay_installment

@login_required
def transaction_create(request, tx_type):
    household = request.user.household
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, household=household, tx_type=tx_type)
        if form.is_valid():
            data = form.cleaned_data
            create_transaction(
                household=household,
                concept=data['concept'],
                amount=data['amount'],
                date=data['date'],
                account=data['account'],
                category=data['category'],
                member=data['member'],
                description=data['description']
            )
            return redirect('dashboard')
    else:
        form = TransactionForm(household=household, tx_type=tx_type, initial={'date': datetime.date.today()})
        
    return render(request, 'transactions/transaction_form.html', {
        'form': form,
        'tx_type': tx_type,
        'title': 'Registrar Ingreso' if tx_type == 'ingreso' else 'Registrar Gasto'
    })

@login_required
def transfer_create(request):
    household = request.user.household
    
    if request.method == 'POST':
        form = TransferForm(request.POST, household=household)
        if form.is_valid():
            data = form.cleaned_data
            try:
                create_transfer(
                    household=household,
                    origin_account=data['origin_account'],
                    destination_account=data['destination_account'],
                    amount=data['amount'],
                    date=data['date'],
                    description=data['description']
                )
                return redirect('dashboard')
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = TransferForm(household=household, initial={'date': datetime.date.today()})
        
    return render(request, 'transactions/transfer_form.html', {
        'form': form,
        'title': 'Registrar Transferencia'
    })

@login_required
def account_list(request):
    household = request.user.household
    accounts = Account.objects.filter(household=household, is_active=True)
    
    accounts_data = []
    for acc in accounts:
        accounts_data.append({
            'obj': acc,
            'balance': get_account_balance(acc)
        })
        
    return render(request, 'accounts/account_list.html', {
        'accounts': accounts_data
    })

@login_required
def obligation_list(request):
    household = request.user.household
    obligations = Obligation.objects.filter(household=household).prefetch_related('installments').order_by('-created_at')
    
    return render(request, 'obligations/obligation_list.html', {
        'obligations': obligations
    })

@login_required
def obligation_create(request):
    household = request.user.household
    if request.method == 'POST':
        form = ObligationForm(request.POST, household=household)
        if form.is_valid():
            d = form.cleaned_data
            create_obligation_with_installments(
                household=household,
                concept=d['concept'],
                creditor=d['creditor'],
                total_amount=d['total_amount'],
                installments_count=d['installments_count'],
                category=d['category'],
                first_due_date=d['first_due_date']
            )
            return redirect('obligation_list')
    else:
        form = ObligationForm(household=household, initial={'first_due_date': datetime.date.today()})
        
    return render(request, 'obligations/obligation_form.html', {
        'form': form,
        'title': 'Registrar Nueva Deuda/Obligación'
    })

@login_required
def installment_pay(request, pk):
    household = request.user.household
    installment = ObligationInstallment.objects.select_related('obligation').get(id=pk, obligation__household=household)
    
    if request.method == 'POST':
        form = InstallmentPayForm(request.POST, household=household)
        if form.is_valid():
            try:
                pay_installment(
                    installment_id=installment.id,
                    account=form.cleaned_data['account'],
                    date=form.cleaned_data['date'],
                    member=None
                )
                return redirect('obligation_list')
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = InstallmentPayForm(household=household, initial={'date': datetime.date.today()})
        
    return render(request, 'obligations/installment_pay.html', {
        'form': form,
        'installment': installment
    })


from finance.models import Budget
from finance.forms import BudgetForm
from finance.services.budgets import get_budget_usage

@login_required
def budget_list(request):
    household = request.user.household
    today = datetime.date.today()
    
    # Filtramos por defecto los presupuestos del mes y año actuales
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    budgets = Budget.objects.filter(household=household, month=month, year=year).select_related('category')
    
    budgets_data = []
    for b in budgets:
        usage = get_budget_usage(b)
        budgets_data.append({
            'budget': b,
            'limit': usage['limit'],
            'spent': usage['spent'],
            'available': usage['available'],
            'percentage': usage['percentage'],
            'status_color': 'var(--verde-positivo)' if usage['percentage'] < 75 else ('var(--naranja-alerta)' if usage['percentage'] <= 100 else 'var(--rojo-error)')
        })
        
    return render(request, 'budgets/budget_list.html', {
        'budgets_data': budgets_data,
        'current_month': month,
        'current_year': year,
    })

@login_required
def budget_create(request):
    household = request.user.household
    today = datetime.date.today()
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, household=household)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.household = household
            try:
                budget.save()
                return redirect('budget_list')
            except Exception as e:
                form.add_error(None, "Ya existe un presupuesto para esta categoría en ese mes y año.")
    else:
        form = BudgetForm(household=household, initial={'month': today.month, 'year': today.year})
        
    return render(request, 'budgets/budget_form.html', {
        'form': form,
        'title': 'Definir Presupuesto'
    })


@login_required
def transaction_report(request):
    household = request.user.household
    transactions = FinancialTransaction.objects.filter(household=household).order_by('-date', '-id')
    
    # Captura de filtros
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    account_id = request.GET.get('account')
    category_type = request.GET.get('type')
    
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
    if account_id:
        transactions = transactions.filter(account_id=account_id)
    if category_type:
        transactions = transactions.filter(category__type=category_type)
        
    # Lógica de Exportación CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="movimientos_bolsillofamiliar.csv"'
        
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Fecha', 'Concepto', 'Cuenta', 'Categoria', 'Tipo', 'Importe', 'Integrante', 'Anulada'])
        
        for tx in transactions:
            writer.writerow([
                tx.date.strftime('%Y-%m-%d'),
                tx.concept,
                tx.account.name,
                tx.category.name,
                tx.category.get_type_display(),
                tx.amount,
                tx.member.name if tx.member else 'N/A',
                'Si' if tx.is_voided else 'No'
            ])
        return response
        
    # Datos para los selectores del formulario de filtro
    accounts = Account.objects.filter(household=household, is_active=True)
    
    return render(request, 'reports/transaction_report.html', {
        'transactions': transactions,
        'accounts': accounts,
        'filters': request.GET,
    })
