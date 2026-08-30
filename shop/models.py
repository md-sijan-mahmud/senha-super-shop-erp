from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="ক্যাটাগরির নাম")

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="পণ্যের নাম")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ক্যাটাগরি")
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ক্রয় মূল্য")
    sell_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="বিক্রয় মূল্য")
    stock_quantity = models.IntegerField(default=0, verbose_name="স্টক পরিমাণ")

    def __str__(self):
        return f"{self.name} - ৳{self.sell_price}"

class ServiceOrder(models.Model):
    customer_name = models.CharField(max_length=150, verbose_name="কাস্টমারের নাম")
    customer_phone = models.CharField(max_length=15, verbose_name="মোবাইল নম্বর")
    service_details = models.TextField(verbose_name="কাজের বিবরণ")
    total_bill = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="মোট বিল")
    advance_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="অগ্রিম পরিশোধ")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="তারিখ")
    is_delivered = models.BooleanField(default=False, verbose_name="ডেলিভারি হয়েছে কি?")

    def __str__(self):
        return f"{self.customer_name} - {self.service_details}"

class Expense(models.Model):
    title = models.CharField(max_length=200, verbose_name="খরচের খাত")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="টাকার পরিমাণ")
    date = models.DateField(auto_now_add=True, verbose_name="তারিখ")

    def __str__(self):
        return f"{self.title} - ৳{self.amount}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('Sale', 'পণ্য বিক্রি'),
        ('Service', 'কম্পিউটার/মগ প্রিন্ট ও সার্ভিস'),
        ('MFS', 'মোবাইল ব্যাংকিং (বিকাশ/নগদ) আয়'),
    )
    trans_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="লেনদেনের ধরণ")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="পণ্য")
    service_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="সার্ভিসের নাম (যেমন: মগ প্রিন্ট)")
    quantity = models.IntegerField(default=1, verbose_name="পরিমাণ")
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="ক্রয় মূল্য (মোট)")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="বিক্রয়/আয় মূল্য (মোট)")
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="লাভ/ক্ষতি")
    note = models.TextField(blank=True, null=True, verbose_name="নোট")
    created_at = models.DateField(auto_now_add=True, verbose_name="তারিখ")

    def save(self, *args, **kwargs):
        # লেনদেন এডিট বা সেভ করার সময় পণ্য বিক্রির ক্ষেত্রে লাভ স্বয়ংক্রিয়ভাবে আপডেট হবে
        if self.trans_type == 'Sale':
            self.profit = self.amount - self.buy_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.trans_type} - ৳{self.amount}"


# নতুন কাস্টমার ও বাকি খাতা ম্যানেজমেন্ট মডেলসমূহ
class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name="কাস্টমারের নাম")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="মোবাইল নম্বর (ঐচ্ছিক)")
    created_at = models.DateField(auto_now_add=True, verbose_name="যোগের তারিখ")

    def __str__(self):
        return f"{self.name} {f'({self.phone})' if self.phone else ''}"

    @property
    def total_due(self):
        transactions = self.customertransaction_set.all()
        total_given = sum(t.amount for t in transactions if t.trans_type == 'due_given')
        total_paid = sum(t.amount for t in transactions if t.trans_type == 'due_paid')
        return total_given - total_paid


class CustomerTransaction(models.Model):
    TRANS_TYPES = (
        ('due_given', 'বাকি দেওয়া (Due Given)'),
        ('due_paid', 'টাকা পরিশোধ (Paid)'),
    )
    
    CATEGORY_TYPES = (
        ('Product', 'পণ্য ক্রয় (Product)'),
        ('Printing', 'প্রিন্টিং সার্ভিস (Printing)'),
        ('MFS', 'মোবাইল ব্যাংকিং (MFS)'),
        ('Other', 'অন্যান্য (Other)'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="কাস্টমার")
    trans_type = models.CharField(max_length=20, choices=TRANS_TYPES, default='due_given', verbose_name="লেনদেনের ধরণ")
    category = models.CharField(max_length=20, choices=CATEGORY_TYPES, default='Product', verbose_name="খাত/বিভাগ")
    item_details = models.CharField(max_length=250, verbose_name="পণ্য/সার্ভিসের নাম ও বিবরণ")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="টাকার পরিমাণ")
    note = models.TextField(blank=True, null=True, verbose_name="নোট (ঐচ্ছিক)")
    created_at = models.DateField(auto_now_add=True, verbose_name="তারিখ")

    def __str__(self):
        return f"{self.customer.name} - ৳{self.amount}"