from django import forms
from .models import Bill, Payment

class BillForm(forms.ModelForm):
    """Form for creating/updating bills"""
    
    class Meta:
        model = Bill
        exclude = ['bill_number', 'created_at', 'updated_at', 'paid_amount']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'appointment': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class PaymentForm(forms.ModelForm):
    """Form for recording payments"""
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount
    
    class Meta:
        model = Payment
        exclude = ['payment_id', 'invoice', 'received_by', 'created_at']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
