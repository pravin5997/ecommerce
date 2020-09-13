from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from mptt.models import TreeForeignKey, MPTTModel

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


class Categorys(MPTTModel):
    name = models.CharField(max_length=50)
    parent = TreeForeignKey("self", related_name="category", on_delete=models.CASCADE, null=True, blank=True)
    is_parent = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=255)
    product_attribute = models.ManyToManyField("productattribute")

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=55)
    subcategory = models.ForeignKey(Categorys, related_name="product_subcategory", on_delete=models.CASCADE)
    description = models.TextField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(blank=True, upload_to='product/', null=True)
    status = models.BooleanField(default=True)
    product_type = models.ForeignKey(ProductType, related_name="product_type", on_delete=models.CASCADE)
    product = models.ForeignKey("self", related_name="parent", on_delete= models.CASCADE, null=True, blank=True)
    is_parent = models.BooleanField()
    
    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

  
class ProductAttributeValue(models.Model):
    name = models.CharField(max_length=50)
    product_attribute = models.ForeignKey(ProductAttribute, related_name="product_attribute_value", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="product_attr_val", on_delete= models.CASCADE)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    cart = models.ForeignKey("Cart", related_name="cart_item", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="product_item", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.id}"
        


class Cart(models.Model):
    user = models.ForeignKey(User, related_name="user_cart", on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.BooleanField(default=True)
    shipping_address = models.ForeignKey('Address', related_name='cart_shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey('Address', related_name='cart_billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('CouponCode', related_name="cart_coupon", on_delete=models.CASCADE, blank=True, null=True)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for item in self.cart_item.all():
            total += item.sub_total
        if self.coupon and self.total_discount:
            total -= self.total_discount
        return total
     


class Order(models.Model):
    user = models.ForeignKey(User, related_name="user_order", on_delete=models.CASCADE)
    created_date_time = models.DateTimeField(auto_now_add=True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.CASCADE, blank=True, null=True)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.CASCADE, blank=True, null=True)
    coupon = models.ForeignKey('CouponCode', related_name="order_coupon", on_delete=models.CASCADE, blank=True, null=True)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    

    def __str__(self):
        return "{}".format(self.user)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="ordered", on_delete=models.CASCADE)
    cart_item = models.ForeignKey(CartItem, related_name="cart_items", on_delete=models.CASCADE, default=1)
    total = models.IntegerField()
    


class Address(models.Model):
    user = models.ForeignKey(User, related_name="adress", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, default="")
    last_name = models.CharField(max_length=50, default="")
    mobile = models.CharField(max_length=15, default="")
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=55)
    state = models.CharField(max_length=55)
    zip_code = models.IntegerField()
    address_type = models.CharField(max_length=1, default="S", choices=ADDRESS_CHOICES)

    def __str__(self):
        return "{} - {}".format(self.street, self.city)


class CouponCode(models.Model):
    DISCOUNT_CHOICES = (
        ('R', 'Rupees'),
        ('P', 'Percent'),
    )
    code = models.CharField(max_length=10, unique=True)
    code_description = models.TextField(max_length=100, default="")
    valid_from = models.DateField(auto_now=False)
    valid_To = models.DateField(auto_now=False)
    discount = models.DecimalField(default= 0, max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    discount_type = models.CharField(max_length=1, default="R", choices=DISCOUNT_CHOICES)
    max_discount = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def __str__(self):
        return self.code


class UserCoupon(models.Model):
    user = models.ForeignKey(User, related_name="user_coupon", on_delete=models.CASCADE)
    coupon = models.ForeignKey(CouponCode, related_name="coupon_code", on_delete=models.CASCADE)
    is_place_order = models.BooleanField(default=False)


class Payment(models.Model):
    user = models.ForeignKey(User, related_name="user_payment", on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, related_name="payment_order", on_delete=models.CASCADE, default=1)
    total_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.total_price


class PaymentOption(models.Model):
    option = models.CharField(max_length=55)
    
    def __str__(self):
        return self.option


    







