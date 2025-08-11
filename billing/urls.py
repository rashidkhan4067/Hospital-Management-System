from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.BillListView.as_view(), name='bill_list'),
    path('create/', views.BillCreateView.as_view(), name='bill_create'),
    path('<int:pk>/', views.BillDetailView.as_view(), name='bill_detail'),
    path('<int:pk>/edit/', views.BillUpdateView.as_view(), name='bill_edit'),
    path('<int:pk>/payment/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('<int:pk>/invoice/', views.InvoiceView.as_view(), name='invoice'),
    path('my-bills/', views.MyBillsView.as_view(), name='my_bills'),
    path('reports/', views.BillingReportView.as_view(), name='billing_reports'),
]
