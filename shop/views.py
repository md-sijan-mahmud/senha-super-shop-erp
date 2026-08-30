from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Transaction, Expense, Customer, CustomerTransaction
from .forms import CustomerForm, CustomerTransactionForm
from django.db.models import Sum
from datetime import date, datetime, timedelta
import csv
from django.http import HttpResponse

def dashboard(request):
    selected_date = request.GET.get('date')
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    
    # ডিফল্টভাবে আজকের তারিখ সিলেক্ট থাকবে যদি অন্য কিছু ফিল্টার না করা হয়
    if not selected_date and not selected_month and not selected_year:
        selected_date = str(date.today())

    transactions = Transaction.objects.all().order_by('-id')
    expenses = Expense.objects.all().order_by('-id')
    
    period_title = "আজকের দিন"

    if selected_date:
        transactions = transactions.filter(created_at=selected_date)
        expenses = expenses.filter(date=selected_date)
        period_title = f"তারিখ: {selected_date}"
    elif selected_month:
        year, month = selected_month.split('-')
        transactions = transactions.filter(created_at__year=year, created_at__month=month)
        expenses = expenses.filter(date__year=year, date__month=month)
        period_title = f"মাস: {month}, {year}"
    elif selected_year:
        transactions = transactions.filter(created_at__year=selected_year)
        expenses = expenses.filter(date__year=selected_year)
        period_title = f"বছর: {selected_year}"
        
    total_sales = transactions.filter(trans_type='Sale').aggregate(Sum('amount'))['amount__sum'] or 0
    total_service = transactions.filter(trans_type='Service').aggregate(Sum('amount'))['amount__sum'] or 0
    total_mfs = transactions.filter(trans_type='MFS').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_profit_sum = transactions.aggregate(Sum('profit'))['profit__sum'] or 0
    net_profit_after_expense = total_profit_sum - total_expense
    
    low_stock_products = Product.objects.filter(stock_quantity__lte=5)
    
    # ড্যাশবোর্ড গ্রাফের জন্য গত ৭ দিনের ডেটা তৈরি (এখানে __date বাদ দিয়ে শুধু =d করা হয়েছে)
    dates = []
    sales_data = []
    profit_data = []

    for i in range(6, -1, -1):
        d = datetime.today().date() - timedelta(days=i)
        dates.append(d.strftime('%Y-%m-%d'))
        
        day_sales = Transaction.objects.filter(created_at=d, trans_type='Sale').aggregate(Sum('amount'))['amount__sum'] or 0
        day_profit = Transaction.objects.filter(created_at=d).aggregate(Sum('profit'))['profit__sum'] or 0
        
        sales_data.append(float(day_sales))
        profit_data.append(float(day_profit))
    
    context = {
        'transactions': transactions,
        'expenses': expenses,
        'selected_date': selected_date,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'period_title': period_title,
        'total_sales': total_sales,
        'total_service': total_service,
        'total_mfs': total_mfs,
        'total_expense': total_expense,
        'total_profit': net_profit_after_expense,
        'low_stock_products': low_stock_products,
        'dates': dates,
        'sales_data': sales_data,
        'profit_data': profit_data,
    }
    return render(request, 'shop/dashboard.html', context)


# আলাদা অ্যানালিটিক্স পেজ ভিউ (সাইডবার মেনুর জন্য)
def analytics_report(request):
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    
    transactions = Transaction.objects.all().order_by('-id')
    expenses = Expense.objects.all().order_by('-id')
    period_title = "মাস বা বছর নির্বাচন করুন"
    
    if selected_month:
        year, month = selected_month.split('-')
        transactions = transactions.filter(created_at__year=year, created_at__month=month)
        expenses = expenses.filter(date__year=year, date__month=month)
        period_title = f"মাস: {month}, {year}"
    elif selected_year:
        transactions = transactions.filter(created_at__year=selected_year)
        expenses = expenses.filter(date__year=selected_year)
        period_title = f"বছর: {selected_year}"
        
    total_sales = transactions.filter(trans_type='Sale').aggregate(Sum('amount'))['amount__sum'] or 0
    total_service = transactions.filter(trans_type='Service').aggregate(Sum('amount'))['amount__sum'] or 0
    total_mfs = transactions.filter(trans_type='MFS').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_profit_sum = transactions.aggregate(Sum('profit'))['profit__sum'] or 0
    net_profit_after_expense = total_profit_sum - total_expense
    
    context = {
        'transactions': transactions,
        'expenses': expenses,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'period_title': period_title,
        'total_sales': total_sales,
        'total_service': total_service,
        'total_mfs': total_mfs,
        'total_expense': total_expense,
        'total_profit': net_profit_after_expense,
    }
    return render(request, 'shop/analytics.html', context)


def stock_list(request):
    products = Product.objects.all()
    return render(request, 'shop/stock_list.html', {'products': products})


def make_sale(request):
    products = Product.objects.all()
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        
        if product.stock_quantity >= quantity:
            total_buy_price = product.buy_price * quantity
            total_sell_price = product.sell_price * quantity
            item_profit = total_sell_price - total_buy_price
            
            product.stock_quantity -= quantity
            product.save()
            
            Transaction.objects.create(
                trans_type='Sale',
                product=product,
                quantity=quantity,
                buy_price=total_buy_price,
                amount=total_sell_price,
                profit=item_profit,
                note=f"বিক্রি: {quantity}টি {product.name}"
            )
            return redirect('dashboard')
    return render(request, 'shop/sell.html', {'products': products})


def add_print_service(request):
    if request.method == 'POST':
        service_name = request.POST.get('service_name')
        amount = request.POST.get('amount')
        profit = request.POST.get('profit', amount)
        note = request.POST.get('note')
        if service_name and amount:
            Transaction.objects.create(
                trans_type='Service',
                service_name=service_name,
                amount=amount,
                profit=profit,
                note=note
            )
            return redirect('dashboard')
    return render(request, 'shop/add_print_service.html')


def add_mfs(request):
    if request.method == 'POST':
        mfs_type = request.POST.get('mfs_type')
        amount = request.POST.get('amount')
        profit = request.POST.get('profit')
        note = request.POST.get('note')
        if mfs_type and amount:
            Transaction.objects.create(
                trans_type='MFS',
                service_name=mfs_type,
                amount=amount,
                profit=profit,
                note=note
            )
            return redirect('dashboard')
    return render(request, 'shop/add_mfs.html')


def add_expense(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        if title and amount:
            Expense.objects.create(title=title, amount=amount)
            return redirect('dashboard')
    return render(request, 'shop/add_expense.html')


def export_excel(request):
    selected_date = request.GET.get('date')
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    
    transactions = Transaction.objects.all()
    expenses = Expense.objects.all()
    file_title = "analytics_report"
    
    if selected_date:
        transactions = transactions.filter(created_at=selected_date)
        expenses = expenses.filter(date=selected_date)
        file_title = f"report_{selected_date}"
    elif selected_month:
        year, month = selected_month.split('-')
        transactions = transactions.filter(created_at__year=year, created_at__month=month)
        expenses = expenses.filter(date__year=year, date__month=month)
        file_title = f"report_month_{selected_month}"
    elif selected_year:
        transactions = transactions.filter(created_at__year=selected_year)
        expenses = expenses.filter(date__year=selected_year)
        file_title = f"report_year_{selected_year}"
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{file_title}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Analytics Report Summary'])
    writer.writerow([])
    
    writer.writerow(['Transactions & Sales Details'])
    writer.writerow(['Date', 'Item/Details', 'Type', 'Quantity', 'Buy Price', 'Amount', 'Profit'])
    for t in transactions:
        name = t.product.name if t.product else (t.service_name or t.note)
        writer.writerow([t.created_at, name, t.trans_type, t.quantity, t.buy_price, t.amount, t.profit])
        
    writer.writerow([])
    writer.writerow(['Expenses Details'])
    writer.writerow(['Date', 'Expense Title', 'Amount'])
    for e in expenses:
        writer.writerow([e.date, e.title, e.amount])
        
    total_profit_sum = transactions.aggregate(Sum('profit'))['profit__sum'] or 0
    total_expense_sum = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    net_profit = total_profit_sum - total_expense_sum
    
    writer.writerow([])
    writer.writerow(['Summary Report'])
    writer.writerow(['Total Net Profit / (Loss)', net_profit])
    writer.writerow(['Total Expense', total_expense_sum])
        
    return response


def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        if transaction.trans_type == 'Sale':
            transaction.quantity = int(request.POST.get('quantity', transaction.quantity))
            transaction.buy_price = float(request.POST.get('buy_price', transaction.buy_price))
            transaction.amount = float(request.POST.get('amount', transaction.amount))
            transaction.profit = transaction.amount - transaction.buy_price
        else:
            transaction.service_name = request.POST.get('service_name', transaction.service_name)
            transaction.amount = float(request.POST.get('amount', transaction.amount))
            transaction.profit = float(request.POST.get('profit', transaction.amount))
        transaction.save()
        return redirect('dashboard')
    return render(request, 'shop/edit_transaction.html', {'transaction': transaction})


# কাস্টমার ও বাকি খাতা ম্যানেজমেন্ট ভিউসমূহ
def customer_list(request):
    query = request.GET.get('q', '')
    if query:
        customers = Customer.objects.filter(name__icontains=query) | Customer.objects.filter(phone__icontains=query)
    else:
        customers = Customer.objects.all().order_by('-id')
    
    form = CustomerForm()
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
            
    context = {
        'customers': customers,
        'form': form,
        'query': query,
    }
    return render(request, 'shop/customer_list.html', context)


def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    transactions = customer.customertransaction_set.all().order_by('-created_at', '-id')
    
    form = CustomerTransactionForm()
    if request.method == 'POST':
        form = CustomerTransactionForm(request.POST)
        if form.is_valid():
            trans = form.save(commit=False)
            trans.customer = customer
            trans.save()
            return redirect('customer_detail', pk=customer.pk)
            
    context = {
        'customer': customer,
        'transactions': transactions,
        'form': form,
    }
    return render(request, 'shop/customer_detail.html', context)