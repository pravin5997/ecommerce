from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse, HttpResponseRedirect
from django.views.generic import View, TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from .models import Product, Cart, CartItem, ProductAttributeValue, Order, ProductAttribute, ProductType, CouponCode, UserCoupon, Categorys, Address, Payment, PaymentOption, OrderItem
from .forms import AddressForm
from decimal import *
from django.urls import reverse_lazy, reverse
from django.core import serializers
from django.template.loader import render_to_string
from django.contrib import messages
from datetime import datetime
from django.template import RequestContext
from django.contrib.auth.models import User
import json
import shopping.context_processors as shopping_context
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY 
    

class ProductFilter(View):
    
    def get(self, request, pk):
        category_obj = Categorys.objects.get(id=pk)
        categorys_list = category_obj.get_descendants(include_self=True)
        pro_obj_list = list(Product.objects.filter(subcategory__in=categorys_list).values_list("id", flat = True))
        prod_attr_list = request.GET.getlist("pro_attr_val[]")
        
        if prod_attr_list:
            all_prod_list = list(ProductAttributeValue.objects.filter(name__in=prod_attr_list).filter(product__in=pro_obj_list).values_list("product_id", flat=True))
            parent_id = list(set(Product.objects.filter(id__in=all_prod_list).values_list("product_id", flat=True)))
            parent_pro = Product.objects.filter(id__in=parent_id)
            data_string = render_to_string('product.html', {"cat_obj": category_obj, "prod": parent_pro}, request=request)
            return JsonResponse(data={"data_string": data_string})
        else:
            categorys_list = category_obj.get_descendants(include_self=True)
            products_list = Product.objects.filter(subcategory__in=categorys_list)
            data_string = render_to_string('product.html', {"cat_obj": category_obj, "prod":products_list}, request=request)
            return JsonResponse(data={"data_string": data_string})

    
def product_quantity_update(request, product):
    child = request.POST.get("child")
    product_quantity = request.POST.get(product.name.replace(" ", ""))
    if product_quantity is not None:
        child_product = Product.objects.get(id=child)
        sub_total = round(int(child_product.price) * int(product_quantity), 4)
        cart_item_list = CartItem.objects.filter(product=child_product).values_list("product", flat=True)
        if child_product.id not in cart_item_list:
            cart_obj = Cart.objects.get(user = request.user)
            CartItem.objects.create(cart = cart_obj, product = child_product, quantity = product_quantity, price_per_unit= child_product.price, sub_total=sub_total)
        else:
            cart = CartItem.objects.get(product=child_product)
            cart.quantity += int(product_quantity)
            sub_total = round(int(child_product.price) * int(cart.quantity), 4)
            cart.sub_total = sub_total
            cart.save()
    

class ProductCategory(View):
    template_name = "product_category.html"

    def get(self, request, pk):
        category_obj = Categorys.objects.get(id=pk)
        categorys_list = category_obj.get_descendants(include_self=True)
        products_list = Product.objects.filter(subcategory__in=categorys_list)
        product_type = ProductType.objects.filter(name=category_obj.name)
        prod_attr = []
        if product_type:
            for prod_typ in product_type: 
                prod_attr.extend(list(prod_typ.product_attribute.all()))
        return render(request, self.template_name, {"prod": products_list, "cat_obj":category_obj, "pro_attr":prod_attr})

    def post(self, request, pk):
        category_obj = Categorys.objects.get(id=pk)
        categorys_list = category_obj.get_descendants(include_self=True)
        products_list = Product.objects.filter(subcategory__in=categorys_list)
        product_type = ProductType.objects.filter(name=category_obj.name)
        product_attribute = []
        if product_type:
            for prod_typ in product_type: 
                product_attribute.extend(list(prod_typ.product_attribute.all()))
        product_id = request.POST.get("event")
        if product_id:
            product = Product.objects.get(id=product_id)
            return JsonResponse(data={"prod_data": product.price, "parent_prod": product.product.id})
        for product in products_list:
            product_quantity_update(request, product)
        return render(request, self.template_name, {"prod": products_list, "cat_obj":category_obj, "pro_attr":product_attribute})


class ProductView(ListView):
    model = Product
    template_name = "home.html"

    def post(self, request):
        products_list = Product.objects.all()
        product_id = request.POST.get("event")
        if product_id:
            product = Product.objects.get(id=product_id)
            return JsonResponse(data={"prod_data": product.price, "parent_prod": product.product.id})
        for product in products_list:
            product_quantity_update(request, product)
        return render(request, self.template_name, {"object_list": products_list})


class ProductDetailView(DetailView):
    model = Product
    template_name = "product_detail.html"

    def post(self, request, pk):
        product_id = request.POST.get("event")
        if product_id:
            product = Product.objects.get(id=product_id)
            return JsonResponse(data={"prod_data": product.price})  
        product = Product.objects.get(id=pk)
        cart_obj_list = Cart.objects.filter(user=request.user)
        if not cart_obj_list:
            Cart.objects.create(user=request.user)
        product_quantity_update(request, product)
        return render(request, self.template_name, {"product": product})
        
def coupon_validation(request, coupon_obj, cart_object):
    if coupon_obj.discount_type == "P":
        coupon_discount = (coupon_obj.discount / 10)
        total_discount = (cart_object.total / 10) * int(coupon_discount)
        if total_discount > coupon_obj.max_discount:
            total_discount = coupon_obj.max_discount
        cart_object.coupon = coupon_obj
        cart_object.total_discount = total_discount
        cart_object.save()
        return messages.success(request, "Successfully apply coupon code")    
    else:
        if coupon_obj.discount < cart_object.total:
            total_discount = coupon_obj.discount
            cart_object.coupon = coupon_obj
            cart_object.total_discount = total_discount
            cart_object.save()
            return messages.success(request, "Successfully apply coupon code")
        else:
            return messages.info(request, "Please maximum amount is greater than Rs.{}  requared".format(int(coupon_obj.max_discount)))
            

def coupon_update(request, cart_object):
    if cart_object.total_discount:
        if cart_object.total_discount >= cart_object.total:
            cart_object.coupon = None
            cart_object.total_discount = None
            cart_object.save()
    if cart_object.coupon:
            coupon_obj =cart_object.coupon
            if coupon_obj.discount_type == "P":
                coupon_discount = (coupon_obj.discount / 10)
                total_discount = (cart_object.total / 10) * int(coupon_discount)
                if total_discount > coupon_obj.max_discount:
                    total_discount = coupon_obj.max_discount
                cart_object.coupon = coupon_obj
                cart_object.total_discount = total_discount
                cart_object.save()


class CartItemList(ListView):
    model = CartItem
    template_name = "cart_list.html"

    def get(self, request):
        cart_object = Cart.objects.get(user=request.user)  
        cart_object.total = cart_object.get_sub_total()
        cart_object.save()
        coupon_update(request, cart_object)
        cart_id = request.GET.get("cart_id")
        cart_qtns = request.GET.get("cart_qtn")
        if cart_id and cart_qtns:
            current_cart_obj = CartItem.objects.get(id=cart_id)
            current_cart_obj.quantity = int(cart_qtns)
            current_cart_obj.sub_total = current_cart_obj.get_product_sub_total(int(cart_qtns))
            current_cart_obj.save()
            cart_object.total = cart_object.get_sub_total()
            cart_object.save()
            coupon_update(request, cart_object)
            return JsonResponse(data = {"cart_id":current_cart_obj.id, "cart_sub_total_price":cart_object.get_sub_total(), "cart_total_price":cart_object.get_total(),"total_discounts":cart_object.total_discount, "cart_sub_total":current_cart_obj.sub_total, "cart_quantity":current_cart_obj.quantity})
        cart_item_id= request.GET.get('id', None)
        if cart_item_id:
            CartItem.objects.get(id=cart_item_id).delete()
            cart_item_obj = CartItem.objects.filter(cart=cart_object)
            if len(cart_item_obj) == 0:
                cart_object.total = 0
                cart_object.save()
            cart_object.total = cart_object.get_sub_total()
            cart_object.save()
            coupon_update(request, cart_object)
            data = {
                'id': cart_item_id,
                "cart_item": len(cart_item_obj),
                "cart_sub_total": cart_object.get_sub_total(),
                "cart_total":cart_object.get_total(),
                "cart_discount":cart_object.total_discount
            }
            return JsonResponse(data)
        return render(request, self.template_name, {"cart_object": cart_object})
    
    def post(self, request):
        cart_object = Cart.objects.get(user=request.user)
        cart_object.total = cart_object.get_sub_total()
        cart_object.save()
        coupon_update(request, cart_object)
      
        my_coupon = request.POST.get("coupon")
        if my_coupon:
            coupon_code = CouponCode.objects.filter(code=my_coupon.upper())
            if coupon_code:
                coupon_obj = CouponCode.objects.get(code=my_coupon.upper())
                today_date = datetime.today().strftime('%Y-%m-%d')
                if today_date >= coupon_obj.valid_from.strftime('%Y-%m-%d') and today_date <= coupon_obj.valid_To.strftime('%Y-%m-%d'):
                    user_coupons = UserCoupon.objects.filter(user=request.user, coupon = coupon_obj)
                    if user_coupons:
                        for my_oderd_coupon in user_coupons:
                            if my_oderd_coupon.is_place_order == True:
                                messages.warning(request, "This coupon code is already applied")
                            else:
                                coupon_validation(request, coupon_obj, cart_object)  
                    else:
                        UserCoupon.objects.create(user=request.user, coupon=coupon_obj)
                        coupon_validation(request, coupon_obj, cart_object)    
                else:
                    messages.warning(request, "Please enter valid coupon")
            else:
                messages.warning(request, "Please enter true coupon")
        return render(request, self.template_name, {"cart_object": cart_object})
      

class ShippingAddress(View):
    def get(self, request):
        address_object = Address.objects.filter(user=self.request.user)
        ship_addr_obj = address_object.filter(address_type="S")
        cart = Cart.objects.get(user=request.user)
        cart_item = cart.cart_item.all()
        form = AddressForm()
        full_ship_ads = request.GET.get("shipping_address")
        if full_ship_ads:    
            cart.shipping_address = Address.objects.get(id = int(full_ship_ads))
            cart.save()
            messages.success(request, "Your Shipping Address Successfully Added")
            return redirect("billing_address")
        return render(request, "shipping_address.html", {'form': form, "cart": cart, "ship_addr_obj": ship_addr_obj, "cart_item":cart_item})

    def post(self, request):
        form = AddressForm(self.request.POST or None)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            mobile = form.cleaned_data['mobile']
            street = form.cleaned_data['street']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            addr_create = Address(user=request.user, first_name=first_name, last_name=last_name, mobile=mobile, street=street, city=city, state=state, zip_code=zip_code, address_type="S")
            addr_create.save()
        address_object = Address.objects.filter(user=self.request.user)
        ship_addr_obj = address_object.filter(address_type="S")
        cart = Cart.objects.get(user=request.user)
        cart_item = cart.cart_item.all()
        messages.success(request, "Your New Shipping address create successfully")
        return render(request, "shipping_address.html", {'form': form, "cart": cart, "ship_addr_obj": ship_addr_obj, "cart_item":cart_item})    

        
class BillingAddress(View):
    def get(self, request):
        address_object = Address.objects.filter(user=self.request.user)
        billing_addr_obj = address_object.filter(address_type="B")
        form = AddressForm()
        cart = Cart.objects.get(user=request.user)
        cart_item = cart.cart_item.all()
        if cart.shipping_address == None:
            return redirect("shipping_address")
        full_bill_ads = request.GET.get("billing_address")
        if full_bill_ads:                
            cart.billing_address = Address.objects.get(id = int(full_bill_ads))
            cart.save()
            messages.success(request, "Your Billing Address Successfully Added")
            return redirect("payment")
        return render(request, "billing_address.html", {'form': form, "cart": cart, "billing_addr_obj": billing_addr_obj, "cart_item":cart_item})

    def post(self, request):
        form = AddressForm(self.request.POST or None)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            mobile = form.cleaned_data['mobile']
            street = form.cleaned_data['street']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            addr_create = Address(user=request.user, first_name=first_name, last_name=last_name, mobile=mobile, street=street, city=city, state=state, zip_code=zip_code, address_type="B")
            addr_create.save()
        address_object = Address.objects.filter(user=self.request.user)
        billing_addr_obj = address_object.filter(address_type="B")
        cart = Cart.objects.get(user=request.user)
        cart_item = cart.cart_item.all()
        messages.success(request, "Your New Billing address create successfully")
        return render(request, "billing_address.html", {'form': form, "cart": cart, "billing_addr_obj": billing_addr_obj, "cart_item":cart_item})


class RemoveCode(View):
    def get(self, request, pk):
        cart_obj = Cart.objects.get(id=pk)
        cart_obj.coupon = None
        cart_obj.total_discount = None
        cart_obj.save()
        return redirect("cartlists")
          

class PaymentMethod(TemplateView):
    template_name = 'payment_option.html'

    def get_context_data(self, **kwargs): # new
        context = super().get_context_data(**kwargs)
        context["cart"] = Cart.objects.get(user=self.request.user)
        context["cart_item"] =  context["cart"].cart_item.all()
        if context["cart"].billing_address == None:
            return redirect("shipping_address")
        return context
        
        
@csrf_exempt
def createpayment(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    cart = Cart.objects.get(user=request.user)
    
    if request.method == "POST":
        intent = stripe.PaymentIntent.create(
            amount=int(cart.get_total()*100),
            currency="inr",
            )
        return JsonResponse({'publishableKey': settings.STRIPE_PUBLISHABLE_KEY, 'clientSecret': intent.client_secret})


class Paymentcomplete(View):

    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.filter(cart=cart)
        order_id = Order(user=request.user, shipping_address = cart.shipping_address, billing_address= cart.billing_address, total_discount= cart.total_discount, total = cart.total, coupon = cart.coupon, sub_total =cart.get_total())
        order_id.save()
        for cart_item_id in cart_item:
            order_item = OrderItem(order=order_id, product=cart_item_id.product, quantity=cart_item_id.quantity, sub_total=cart_item_id.sub_total, price_per_unit=cart_item_id.price_per_unit)
            order_item.save()
        user_coupon = UserCoupon.objects.filter(coupon=cart.coupon)
        if user_coupon:
            order_coupon = UserCoupon.objects.get(coupon=cart.coupon)
            order_coupon.is_place_order = True
            order_coupon.save()
            cart.coupon = None
        cart.total = 0
        cart.total_discount = None
        cart.save()
        cart_item.delete() 
        data = json.loads(request.POST.get("payload"))
        amount = (data["amount"])/100
        return render(request, "payment-complete.html", {"amount": amount, "order_id":order_id})
        

class OrderList(ListView):
    model = OrderItem
    template_name = "my_order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = list(Order.objects.filter(user = self.request.user).values_list("id", flat=True))
        context['order_item'] = OrderItem.objects.filter(order__in=order).order_by("-order_date")
        return context

        
class OrderDetail(DetailView):
    model = Order
    template_name = "order_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_detail'] = Order.objects.get(id=self.kwargs['pk'])
        return context