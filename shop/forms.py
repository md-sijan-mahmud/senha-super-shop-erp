from django import forms
from .models import Customer, CustomerTransaction

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone']  # এখানে শুধু name এবং phone থাকবে
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'কাস্টমারের নাম লিখুন'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'মোবাইল নম্বর (ঐচ্ছিক)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False

class CustomerTransactionForm(forms.ModelForm):
    class Meta:
        model = CustomerTransaction
        fields = ['trans_type', 'category', 'item_details', 'amount', 'note']
        widgets = {
            'trans_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'item_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'যেমন: টি-শার্ট (৫০০ টাকা) বা বিকাশ ক্যাশআউট'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'টাকার পরিমাণ'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'অতিরিক্ত কোনো কথা থাকলে... (ঐচ্ছিক)'}),
        }