from django.db import transaction
from finance.models import FinancialTransaction

@transaction.atomic
def create_transaction(household, concept, amount, date, account, category, member=None, description='', voucher=None):
    """
    Crea un ingreso o gasto validando que pertenezcan al mismo hogar.
    """
    if account.household != household or category.household != household:
        raise ValueError("La cuenta o categoría no pertenece al hogar especificado.")
        
    return FinancialTransaction.objects.create(
        household=household,
        concept=concept,
        amount=amount,
        date=date,
        account=account,
        category=category,
        member=member,
        description=description,
        voucher=voucher
    )

@transaction.atomic
def void_transaction(transaction_id, reason):
    """
    Aplica la Regla de Reversión: marca la transacción como anulada
    y libera la cuota asociada si correspondía a un pago.
    """
    tx = FinancialTransaction.objects.select_related('installment_paid').get(id=transaction_id)
    
    if tx.is_voided:
        raise ValueError("La transacción ya se encuentra anulada.")
        
    tx.is_voided = True
    tx.void_reason = reason
    tx.save()
    
    # Si la transacción era el pago de una cuota, liberamos la cuota
    if hasattr(tx, 'installment_paid') and tx.installment_paid is not None:
        installment = tx.installment_paid
        installment.is_paid = False
        installment.payment_transaction = None
        installment.save()
        
    return tx
