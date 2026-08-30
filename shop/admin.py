from django.contrib import admin
from .models import Category, Product, ServiceOrder, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'buy_price', 'sell_price', 'stock_quantity')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_phone', 'service_details', 'total_bill', 'advance_paid', 'is_delivered', 'order_date')
    list_filter = ('is_delivered', 'order_date')
    search_fields = ('customer_name', 'customer_phone')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('trans_type', 'product', 'quantity', 'amount', 'profit', 'created_at')
    list_filter = ('trans_type', 'created_at')
    search_fields = ('note',)