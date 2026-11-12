from django import forms
from finance.models import FinancialTransaction, Account, Category, Transfer
from core.models import Member

class TransactionForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = ['concept', 'amount', 'date', 'account', 'category', 'member', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'concept': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Compra en el súper'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'account': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'member': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        household = kwargs.pop('household')
        tx_type = kwargs.pop('tx_type', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar solo opciones del hogar actual
        self.fields['account'].queryset = Account.objects.filter(household=household, is_active=True)
        self.fields['member'].queryset = Member.objects.filter(household=household, is_active=True)
        
        if tx_type:
            self.fields['category'].queryset = Category.objects.filter(household=household, type=tx_type)
        else:
            self.fields['category'].queryset = Category.objects.filter(household=household)

class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['origin_account', 'destination_account', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'origin_account': forms.Select(attrs={'class': 'form-control'}),
            'destination_account': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        household = kwargs.pop('household')
        super().__init__(*args, **kwargs)
        
        # Filtrar solo cuentas activas del hogar
        qs = Account.objects.filter(household=household, is_active=True)
        self.fields['origin_account'].queryset = qs
        self.fields['destination_account'].queryset = qs

class ObligationForm(forms.Form):
    concept = forms.CharField(label='Concepto', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Préstamo Personal'}))
    creditor = forms.CharField(label='Acreedor', max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Banco Macro'}))
    total_amount = forms.DecimalField(label='Importe Total', max_digits=14, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    installments_count = forms.IntegerField(label='Cantidad de Cuotas', min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(label='Categoría de Gasto', queryset=Category.objects.none(), widget=forms.Select(attrs={'class': 'form-control'}))
    first_due_date = forms.DateField(label='Primer Vencimiento', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        household = kwargs.pop('household')
        super().__init__(*args, **kwargs)
        # Solo permitimos categorías de tipo 'gasto'
        self.fields['category'].queryset = Category.objects.filter(household=household, type='gasto')

class InstallmentPayForm(forms.Form):
    account = forms.ModelChoiceField(label='Cuenta de Pago', queryset=Account.objects.none(), widget=forms.Select(attrs={'class': 'form-control'}))
    date = forms.DateField(label='Fecha de Pago', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        household = kwargs.pop('household')
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(household=household, is_active=True)


from finance.models import Budget

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'month', 'year', 'limit']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2020}),
            'limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        household = kwargs.pop('household')
        super().__init__(*args, **kwargs)
        # Solo categorías de tipo gasto
        self.fields['category'].queryset = Category.objects.filter(household=household, type='gasto')
