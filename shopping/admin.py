from django.contrib import admin
from .models import Address, ProductType, Product, ProductAttribute, ProductAttributeValue, Cart, CartItem, Order, CouponCode, UserCoupon, Categorys, OrderItem, Payment, PaymentOption


class CategorysAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_parent",)


class AddressAdmin(admin.ModelAdmin):
    list_display = ("street", "city", "state", "zip_code",)


class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "subcategory", "price", "image", "status", "product_type", "product", "is_parent",)

    
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("name",)


class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("name", "product_attribute", "product")


class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total", "status", "shipping_address", "billing_address", "coupon", "total_discount")


class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "price_per_unit", "sub_total")


class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "valid_from", "valid_To", "discount", "active")

class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "created_date_time", "shipping_address", "billing_address", "coupon", "total_discount")

# Register your models here.
admin.site.register(Address, AddressAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttribute, ProductAttributeAdmin)
admin.site.register(ProductAttributeValue, ProductAttributeValueAdmin)
admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(CouponCode, CouponAdmin)
admin.site.register(UserCoupon)
admin.site.register(Categorys, CategorysAdmin)
admin.site.register(Payment)
admin.site.register(PaymentOption)


