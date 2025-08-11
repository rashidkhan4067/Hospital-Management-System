from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Bill, Payment
from .forms import BillForm, PaymentForm

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'ADMIN'

class BillListView(LoginRequiredMixin, ListView):
    model = Bill
    template_name = 'billing/premium_bill_list.html'
    context_object_name = 'bills'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter based on user role
        if self.request.user.role == 'PATIENT':
            queryset = queryset.filter(patient=self.request.user.patient_profile)
        
        # Search and filter
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if search:
            queryset = queryset.filter(
                Q(bill_number__icontains=search) |
                Q(patient__user__first_name__icontains=search) |
                Q(patient__user__last_name__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
            
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
            
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset.select_related('patient__user').order_by('-created_at')


class BillDetailView(LoginRequiredMixin, DetailView):
    model = Bill
    template_name = 'billing/bill_detail.html'
    context_object_name = 'bill'
    
    def get_queryset(self):
        return super().get_queryset().select_related('patient__user').prefetch_related('payments')


class BillCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Bill
    form_class = BillForm
    template_name = 'billing/bill_form.html'
    success_url = reverse_lazy('billing:bill_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Bill created successfully!')
        return super().form_valid(form)


class BillUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Bill
    form_class = BillForm
    template_name = 'billing/bill_form.html'
    success_url = reverse_lazy('billing:bill_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Bill updated successfully!')
        return super().form_valid(form)


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'billing/payment_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bill'] = get_object_or_404(Bill, pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        bill = get_object_or_404(Bill, pk=self.kwargs['pk'])
        form.instance.bill = bill
        
        # Check if payment amount exceeds remaining amount
        remaining = bill.total_amount - bill.paid_amount
        if form.instance.amount > remaining:
            messages.error(self.request, f'Payment amount cannot exceed remaining amount: ${remaining}')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Payment recorded successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('billing:bill_detail', kwargs={'pk': self.kwargs['pk']})


class InvoiceView(LoginRequiredMixin, DetailView):
    model = Bill
    template_name = 'billing/invoice.html'
    context_object_name = 'bill'
    
    def get_queryset(self):
        return super().get_queryset().select_related('patient__user').prefetch_related('payments')


class MyBillsView(LoginRequiredMixin, ListView):
    model = Bill
    template_name = 'billing/my_bills.html'
    context_object_name = 'bills'
    paginate_by = 10
    
    def get_queryset(self):
        if self.request.user.role == 'PATIENT':
            return Bill.objects.filter(
                patient=self.request.user.patient_profile
            ).select_related('patient__user').order_by('-created_at')
        return Bill.objects.none()


class BillingReportView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'billing/billing_reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range
        today = timezone.now().date()
        start_date = today - timedelta(days=30)
        
        # Get billing statistics
        bills = Bill.objects.filter(created_at__date__gte=start_date)
        
        total_revenue = bills.aggregate(total=Sum('total_amount'))['total'] or 0
        total_paid = bills.aggregate(total=Sum('paid_amount'))['total'] or 0
        total_pending = total_revenue - total_paid
        
        # Monthly breakdown
        monthly_data = []
        for i in range(30):
            date = today - timedelta(days=i)
            day_bills = bills.filter(created_at__date=date)
            daily_total = day_bills.aggregate(total=Sum('total_amount'))['total'] or 0
            daily_paid = day_bills.aggregate(total=Sum('paid_amount'))['total'] or 0
            
            monthly_data.append({
                'date': date,
                'total': daily_total,
                'paid': daily_paid,
                'pending': daily_total - daily_paid
            })
        
        context.update({
            'total_revenue': total_revenue,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'monthly_data': monthly_data,
            'recent_bills': bills.order_by('-created_at')[:10]
        })
        return context
