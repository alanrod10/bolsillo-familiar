from django.db import models
from core.models import Household, Member

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('efectivo', 'Efectivo'),
        ('banco', 'Cuenta Bancaria'),
        ('billetera', 'Billetera Virtual'),
        ('ahorro', 'Ahorro')
    ]
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    initial_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Category(models.Model):
    TYPE_CHOICES = [('ingreso', 'Ingreso'), ('gasto', 'Gasto')]
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.name} [{self.get_type_display()}]"

class FinancialTransaction(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='transactions')
    concept = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField()
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    member = models.ForeignKey(Member, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)
    voucher = models.FileField(upload_to='uploads/vouchers/', null=True, blank=True)
    
    # Control de reversión
    is_voided = models.BooleanField(default=False)
    void_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.concept} - ${self.amount}"

class Transfer(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='transfers')
    origin_account = models.ForeignKey(Account, related_name='transfers_out', on_delete=models.PROTECT)
    destination_account = models.ForeignKey(Account, related_name='transfers_in', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transferencia: {self.origin_account.name} -> {self.destination_account.name} (${self.amount})"

class Budget(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    limit = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        unique_together = ('category', 'month', 'year')

    def __str__(self):
        return f"Presupuesto {self.category.name} - {self.month}/{self.year}"

class Obligation(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='obligations')
    concept = models.CharField(max_length=255)
    creditor = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    installments_count = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.concept} ({self.creditor})"

class ObligationInstallment(models.Model):
    obligation = models.ForeignKey(Obligation, related_name='installments', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    payment_transaction = models.OneToOneField(
        FinancialTransaction, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='installment_paid'
    )

    def __str__(self):
        return f"Cuota {self.number}/{self.obligation.installments_count} - {self.obligation.concept}"
