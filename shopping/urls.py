from django.urls import path, include
from .views import ProductView, ProductDetailView, CartItemList, ProductFilter, ProductCategory, ShippingAddress, BillingAddress, PaymentMethod, RemoveCode, createpayment, Paymentcomplete, MyOrder, OrderDetail
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", ProductView.as_view(), name="product"),
    path("category/<int:pk>/prod/", ProductFilter.as_view(), name="product_filter"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product_details"),
    path("cartlist/", CartItemList.as_view(), name="cartlists"),
    path("categorys/<int:pk>/", ProductCategory.as_view(), name="testing"),
    # path("address/", Checkout.as_view(), name="address"),
    # path("checkout/", AddressCreate.as_view(), name="checkout"),
    path("shipping-address/", ShippingAddress.as_view(), name="shipping_address"),
    path("billing-address/", BillingAddress.as_view(), name="billing_address"),
    path("payment/", PaymentMethod.as_view(), name="payment"),
    path("cartlist/<int:pk>", RemoveCode.as_view(), name="remove_code"),
    # path("payment-page/", HomePageView.as_view(), name="payment_page"),
    path("order/", MyOrder.as_view(), name="order"),
    path("create-payment-intent", createpayment, name="create-payment-intent"),
    path("payment-complete", Paymentcomplete.as_view(), name="payment-complete"),
    path("order/<int:pk>/", OrderDetail.as_view(), name="order_details"),

    
]+static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)