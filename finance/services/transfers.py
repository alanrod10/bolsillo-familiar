from django.db import transaction
from finance.models import Transfer

@transaction.atomic
def create_transfer(household, origin_account, destination_account, amount, date, description=''):
    """
    Registra una transferencia entre dos cuentas del mismo hogar.
    Validaciones de negocio según reglas establecidas.
    """
    if origin_account == destination_account:
        raise ValueError("La cuenta de origen y destino no pueden ser la misma.")
        
    if origin_account.household != household or destination_account.household != household:
        raise ValueError("Ambas cuentas deben pertenecer al hogar especificado.")
        
    if amount <= 0:
        raise ValueError("El importe de la transferencia debe ser mayor a cero.")
        
    return Transfer.objects.create(
        household=household,
        origin_account=origin_account,
        destination_account=destination_account,
        amount=amount,
        date=date,
        description=description
    )
