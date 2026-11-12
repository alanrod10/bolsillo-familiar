import datetime
from decimal import Decimal, ROUND_DOWN
from django.db import transaction
from finance.models import Obligation, ObligationInstallment
from finance.services.transactions import create_transaction

def add_months(date_obj, months):
    """Función nativa para sumar meses respetando fin de mes."""
    month = date_obj.month - 1 + months
    year = date_obj.year + month // 12
    month = month % 12 + 1
    day = min(date_obj.day, [31, 29 if year % 4 == 0 and not year % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
    return datetime.date(year, month, day)

@transaction.atomic
def create_obligation_with_installments(household, concept, creditor, total_amount, installments_count, category, first_due_date):
    """
    Regla de cuotas: El total se distribuye exactamente.
    Los centavos sobrantes se ajustan en la última cuota.
    """
    if total_amount <= 0 or installments_count <= 0:
        raise ValueError("El importe total y la cantidad de cuotas deben ser mayores a cero.")
        
    obligation = Obligation.objects.create(
        household=household,
        concept=concept,
        creditor=creditor,
        total_amount=total_amount,
        installments_count=installments_count,
        category=category
    )
    
    # División truncando centavos para evitar sobrepasar el total por redondeo
    base_amount = (total_amount / Decimal(installments_count)).quantize(Decimal('.01'), rounding=ROUND_DOWN)
    remainder = total_amount - (base_amount * installments_count)
    
    installments = []
    current_date = first_due_date
    
    for i in range(1, installments_count + 1):
        amount = base_amount
        if i == installments_count:
            amount += remainder # Ajuste en la cuota final
            
        installments.append(ObligationInstallment(
            obligation=obligation,
            number=i,
            amount=amount,
            due_date=current_date
        ))
        current_date = add_months(current_date, 1)
        
    ObligationInstallment.objects.bulk_create(installments)
    return obligation

@transaction.atomic
def pay_installment(installment_id, account, date, member=None):
    """
    Paga una cuota generando un único gasto a través del servicio de transacciones.
    """
    installment = ObligationInstallment.objects.select_related('obligation__household', 'obligation__category').get(id=installment_id)
    
    if installment.is_paid:
        raise ValueError("Esta cuota ya se encuentra pagada.")
        
    concept = f"Pago Cuota {installment.number}/{installment.obligation.installments_count} - {installment.obligation.concept}"
    
    tx = create_transaction(
        household=installment.obligation.household,
        concept=concept,
        amount=installment.amount,
        date=date,
        account=account,
        category=installment.obligation.category,
        member=member,
        description=f"Acreedor: {installment.obligation.creditor}"
    )
    
    installment.is_paid = True
    installment.payment_transaction = tx
    installment.save()
    
    return installment
