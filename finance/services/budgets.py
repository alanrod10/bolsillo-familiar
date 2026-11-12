from decimal import Decimal
from django.db.models import Sum
from finance.models import Budget, FinancialTransaction

def get_budget_usage(budget):
    """
    Calcula el uso de un presupuesto en su mes y año correspondiente.
    Solo considera gastos efectivos (no anulados).
    """
    spent = FinancialTransaction.objects.filter(
        category=budget.category,
        is_voided=False,
        date__year=budget.year,
        date__month=budget.month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    available = budget.limit - spent
    percentage = (spent / budget.limit * 100) if budget.limit > 0 else Decimal('100.00')
    
    return {
        'limit': budget.limit,
        'spent': spent,
        'available': available,
        'percentage': round(percentage, 2)
    }
