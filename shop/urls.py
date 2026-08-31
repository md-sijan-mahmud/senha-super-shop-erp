from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics_report, name='analytics_report'), # নতুন পাথ
    path('sell/', views.make_sale, name='make_sale'),
    path('add-service/', views.add_print_service, name='add_print_service'),
    path('add-mfs/', views.add_mfs, name='add_mfs'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('stock-list/', views.stock_list, name='stock_list'),
    path('export-excel/', views.export_excel, name='export_excel'),
    path('edit-transaction/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customer/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('complete-shift/', views.complete_shift, name='complete_shift'),
]