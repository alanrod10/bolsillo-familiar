from django.urls import path
from . import views

urlpatterns = [
    path('transacciones/nueva/<str:tx_type>/', views.transaction_create, name='transaction_create'),
    path('transferencias/nueva/', views.transfer_create, name='transfer_create'),
    path('cuentas/', views.account_list, name='account_list'),
    path('obligaciones/', views.obligation_list, name='obligation_list'),
    path('obligaciones/nueva/', views.obligation_create, name='obligation_create'),
    path('cuotas/<int:pk>/pagar/', views.installment_pay, name='installment_pay'),
    path('presupuestos/', views.budget_list, name='budget_list'),
    path('presupuestos/nuevo/', views.budget_create, name='budget_create'),
    path('informes/', views.transaction_report, name='transaction_report'),
]
