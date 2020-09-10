from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse
from django.views.generic import View, TemplateView, ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from .models import Product, Cart, CartItem, ProductAttributeValue,Order, ProductAttribute, ProductType, CouponCode, UserCoupon, Categorys, Address, Payment, PaymentOption
from .forms import AddressForm
from decimal import *
from django.urls import reverse_lazy
from django.core import serializers
from django.template.loader import render_to_string
from django.contrib import messages
from datetime import datetime
from django.template import RequestContext
from django.contrib.auth.models import User    
    

class ProductFilter(View):
    
    def get(self, request, pk):
        cates = Categorys.objects.all()
        cat_obj = Categorys.objects.get(id=pk)
        pro_obj_list = list(cat_obj.product_subcategory.all().values_list("id", flat = True))
        if pro_obj_list == []:
            sub_cat = list(cat_obj.category.all().values_list("id", flat=True))
            pro_obj_list = list(Product.objects.filter(subcategory_id__in=sub_cat).values_list("id", flat = True))

        cart_count = CartItem.objects.all()
        prod_attr_list= request.GET.getlist("pro_attr_val[]")
        
        if prod_attr_list:
            all_prod_list = []
            for name in prod_attr_list:
                pro_attr_obj = list(ProductAttributeValue.objects.filter(name=name, product__in=pro_obj_list).values_list("product_id", flat=True))
                all_prod_list.extend(pro_attr_obj)
            parent_id = list(set(Product.objects.filter(id__in=all_prod_list).values_list("product_id", flat=True)))
            parent_pro = Product.objects.filter(id__in=parent_id)
            
            data_string = render_to_string('product.html', {"cates": cates, "cart_count": cart_count, "cat_obj": cat_obj, "prod":parent_pro}, request=request)
            return JsonResponse(data={"data_string": data_string})
        else:
            pro_obj_list = list(cat_obj.product_subcategory.all())
            if pro_obj_list == []:
                sub_cat = list(cat_obj.category.all().values_list("id", flat=True))
                pro_obj_list = Product.objects.filter(subcategory_id__in=sub_cat)
            data_string = render_to_string('product.html', {"cates": cates, "cart_count": cart_count, "cat_obj": cat_obj, "prod":pro_obj_list}, request=request)
            return JsonResponse(data={"data_string": data_string})
        

class ProductCategory(View):
    template_name = "product_category.html"
    def get(self, request, pk):
        cat_obj = Categorys.objects.get(id=pk)
        cates = Categorys.objects.all()
        cart_count = CartItem.objects.all()
        pro_ty = ProductType.objects.filter(name=cat_obj.name)
        pro_attr = []
        if pro_ty:
            for p in pro_ty: 
                pro_attr.extend(list(p.product_attribute.all()))
        pro_obj_list = list(cat_obj.product_subcategory.all())
        if pro_obj_list == []: 
            for k in cat_obj.category.all():
                if list(k.category.all()) != []:
                    for l in list(k.category.all()):
                        if  list(l.category.all()) != []:
                            for m in list(l.category.all()):
                                pro_obj_list.extend(list(m.product_subcategory.all())) 
                        else:
                            pro_obj_list.extend(list(l.product_subcategory.all()))
                else:
                    pro_obj_list.extend(list(k.product_subcategory.all()))
        return render(request, self.template_name, {"prod": pro_obj_list, "cart_count": cart_count, "cates": cates, "cat_obj":cat_obj, "pro_attr":pro_attr})

    def post(self, request, pk):
        cat_obj = Categorys.objects.get(id = pk)
        pro_obj_list = list(cat_obj.product_subcategory.all())
        pro_ty = list(ProductType.objects.filter(name=cat_obj.name))
        pro_attr = []
        if pro_ty != []:
            for p in pro_ty: 
                pro_attr.extend(list(p.product_attribute.all()))
        if pro_obj_list == []:
            pro_obj_list = []
            for k in cat_obj.category.all():
                if list(k.category.all()) != []:
                    for l in list(k.category.all()):
                        if  list(l.category.all()) != []:
                            for m in list(l.category.all()):
                                pro_obj_list.extend(list(m.product_subcategory.all())) 
                        else:
                            pro_obj_list.extend(list(l.product_subcategory.all()))
                else:
                    pro_obj_list.extend(list(k.product_subcategory.all()))
        cart_count = CartItem.objects.all()
        cates = Categorys.objects.all()
        ajax = request.POST.get("event")
        if ajax:
            product = Product.objects.filter(id=ajax)
            prod_data = serializers.serialize('json', product)
            for parent_prod in product:
                return JsonResponse(data={"prod_data": prod_data, "parent_prod": parent_prod.product.id})

        for i in pro_obj_list:
            child = request.POST.get("child")
            qtn = request.POST.get(i.name.replace(" ", ""))
            if qtn is not None:
                child_pr = Product.objects.get(id=child)
                sub_total = round(int(child_pr.price) * int(qtn), 4)
                cart = CartItem.objects.filter(product=child_pr).values_list("product", flat=True)
                if child_pr.id not in cart:
                    cart_obj = Cart.objects.get(user = request.user)
                    CartItem.objects.create(cart = cart_obj, product = child_pr, quantity = qtn, price_per_unit= child_pr.price, sub_total=sub_total)
                else:
                    cart = CartItem.objects.get(product=child_pr)
                    cart.quantity += int(qtn)
                    sub_total = round(int(child_pr.price) * int(cart.quantity), 4)
                    cart.sub_total = sub_total
                    cart.save()
        return render(request, self.template_name, {"prod": pro_obj_list, "cart_count":cart_count, "cates": cates, "cat_obj":cat_obj, "pro_attr":pro_attr})


class ProductView(ListView):
    model = Product
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)
        context['cart_count'] = CartItem.objects.all()
        context["cates"] = Categorys.objects.all()
        return context

    def post(self, request):
        cates = Categorys.objects.all()
        product_obj = Product.objects.all()
        cart_count = CartItem.objects.all()
        ajax = request.POST.get("event")
        if ajax:
            product = Product.objects.filter(id=ajax)
            prod_data = serializers.serialize('json', product)
            for parent_prod in product:
                return JsonResponse(data={"prod_data": prod_data, "parent_prod": parent_prod.product.id})

        for i in product_obj:
            child = request.POST.get("child")
            qtn = request.POST.get(i.name.replace(" ", ""))
            if qtn is not None:
                child_pr = Product.objects.get(id=child)
                sub_total = round(int(child_pr.price) * int(qtn), 4)
                cart = CartItem.objects.filter(product=child_pr).values_list("product", flat=True)
                if child_pr.id not in cart:
                    cart_obj = Cart.objects.get(user = request.user)
                    CartItem.objects.create(cart = cart_obj, product = child_pr, quantity = qtn, price_per_unit= child_pr.price, sub_total=sub_total)
                else:
                    cart = CartItem.objects.get(product=child_pr)
                    cart.quantity += int(qtn)
                    sub_total = round(int(child_pr.price) * int(cart.quantity), 4)
                    cart.sub_total = sub_total
                    cart.save()
        return render(request, self.template_name, {"object_list": product_obj, "cart_count":cart_count, "cates":cates})


class ProductDetailView(DetailView):
    model = Product
    template_name = "product_detail.html"

    def get_object(self):
        return get_object_or_404(Product, pk=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['cart_count'] = CartItem.objects.all()
        context["cates"] = Categorys.objects.all()
        return context

    def post(self, request, pk):
        ajax = request.POST.get("event")
        if ajax:
            product = Product.objects.filter(id=int(ajax))
            prod_data = serializers.serialize('json', product)     
            return JsonResponse(data={"prod_data": prod_data})  
        product = Product.objects.get(id=pk)
        cates = Categorys.objects.all()
        cart_obj = Cart.objects.filter(user=request.user)
        if not cart_obj:
            Cart.objects.create(user=request.user)
        cart_count = CartItem.objects.all()
        cart = Cart.objects.get(user=request.user)
        qtn = request.POST.get(product.name.replace(" ", ""))
        child_p = request.POST.get("child")
        child_product = Product.objects.get(id=child_p)
        sub_total = round(int(child_product.price) * int(qtn), 4)
        cart_item = list(CartItem.objects.filter(cart=cart).values_list("product_id", flat=True))
        if child_product.id not in cart_item:
            CartItem.objects.create(cart=cart, product=child_product, quantity=qtn, price_per_unit=child_product.price, sub_total=sub_total)
        else:
            cart_item_Obj = CartItem.objects.get(product=child_product)
            cart_item_Obj.quantity += int(qtn)
            sub_total = round(int(child_product.price) * int(cart_item_Obj.quantity), 4)
            cart_item_Obj.sub_total = sub_total
            cart_item_Obj.save()
        return render(request, self.template_name, {"product": product, "cart_count": cart_count, "cates": cates})
        
def Coupon_validation(request, coupon_obj, cart_object, order_obj):
    if coupon_obj.discount_type == "P":
        dis = (coupon_obj.discount / 10)
        total_discount = round((cart_object.total / 10) * int(dis))
        if total_discount > coupon_obj.max_discount:
            total_discount = coupon_obj.max_discount
        cart_object.coupon = coupon_obj
        cart_object.total_discount = total_discount
        cart_object.save()
        if order_obj:
            update_oreder = order_obj.get(user=request.user)
            update_oreder.coupon = coupon_obj
            update_oreder.total_discount = total_discount
            update_oreder.save()
        else:
            Order.objects.create(user=request.user, coupon=coupon_obj, total_discount=total_discount)
        return messages.success(request, "Successfully apply coupon code")    
    else:
        if coupon_obj.discount < cart_object.total:
            total_discount = coupon_obj.discount
            cart_object.coupon = coupon_obj
            cart_object.total_discount = total_discount
            cart_object.save()
            if order_obj:
                update_oreder = order_obj.get(user=request.user)
                update_oreder.coupon = coupon_obj
                update_oreder.total_discount = total_discount
                update_oreder.save()
            else:
                Order.objects.create(user = request.user, coupon = coupon_obj, total_discount = total_discount)
            return messages.success(request, "Successfully apply coupon code")
        else:
            return messages.info(request, "Please maximum amount is greater than Rs.{}  requared".format(int(coupon_obj.max_discount))) 


class CartItemList(View):
    model = CartItem
    template_name = "cart_list.html"

    def get(self, request):
        cart = CartItem.objects.all()
        cates = Categorys.objects.all()
        cart_list = list(cart.values_list("id", flat=True))
        cart_object = Cart.objects.get(user=request.user)
        cart_price = 0
        total_discount = 0
        
        if cart_object.total_discount:
            if cart_object.total_discount >= cart_object.total:
                cart_object.coupon = None
                cart_object.total_discount = None
                cart_object.save() 
        for car in cart:
            cart_price += car.sub_total
            cart_object.total = cart_price
            cart_object.save()
        if cart_object.coupon:
            coupon_obj =cart_object.coupon
            if coupon_obj.discount_type == "P":
                dis = (coupon_obj.discount / 10)
                total_discount = round((cart_object.total / 10) * int(dis))
                if total_discount > coupon_obj.max_discount:
                    total_discount = coupon_obj.max_discount
                cart_object.coupon = coupon_obj
                cart_object.total_discount = total_discount
                cart_object.save()
        return render(request, self.template_name, {"cart_count": cart, "cart_object": cart_object, "cates":cates})
    
    def post(self, request):
        cart = CartItem.objects.all()
        cart_object = Cart.objects.get(user=request.user)
        order_obj = Order.objects.filter(user=request.user)
        cates = Categorys.objects.all()
        cart_price = 0
        total_discount = 0
        for car in cart:
            qtn1 = request.POST.get(car.product.name)
            if qtn1 is not None:
                car.quantity = qtn1
                car.sub_total = round(int(car.product.price) * int(qtn1), 4)
                car.save()
            cart_price += car.sub_total
            cart_object.total = cart_price
            cart_object.save()
        if cart_object.total_discount:
            if cart_object.total_discount >= cart_object.total:
                cart_object.coupon = None
                cart_object.total_discount = None
                cart_object.save() 
        sub_total = cart_object.total
        total_price = cart_object.total
        order = request.POST.get("order")
        if order != None:
            co_order = CouponCode.objects.filter(code=order.upper())
            today_date = datetime.today().strftime('%Y-%m-%d')
            for coupon_order in co_order:
                if coupon_order.discount < cart_object.total and today_date >= coupon_order.valid_from.strftime('%Y-%m-%d') and today_date <= coupon_order.valid_To.strftime('%Y-%m-%d'):
                    user_coupon = UserCoupon.objects.get(coupon=coupon_order)
                    user_coupon.is_place_order = True
                    user_coupon.save()
        if request.POST.get("code_remove") == "remove":
            return JsonResponse(data={"total_price": total_price})
        if cart_object.coupon:
            coupon_obj =cart_object.coupon
            if coupon_obj.discount_type == "P":
                dis = (coupon_obj.discount / 10)
                total_discount = round((cart_object.total / 10) * int(dis))
                if total_discount > coupon_obj.max_discount:
                    total_discount = coupon_obj.max_discount
                cart_object.coupon = coupon_obj
                cart_object.total_discount = total_discount
                cart_object.save()
        cou = request.POST.get("coupon")
        if cou:
            coupon_code = CouponCode.objects.filter(code=cou.upper())
            if coupon_code:
                coupon_obj = CouponCode.objects.get(code=cou.upper())
                today_date = datetime.today().strftime('%Y-%m-%d')
                if today_date >= coupon_obj.valid_from.strftime('%Y-%m-%d') and today_date <= coupon_obj.valid_To.strftime('%Y-%m-%d'):
                    user_coupons = UserCoupon.objects.filter(user=request.user, coupon = coupon_obj)
                    if user_coupons:
                        for my_oderd_coupon in user_coupons:
                            if my_oderd_coupon.is_place_order == True:
                                messages.warning(request, "This coupon code is already applied")
                            else:
                                Coupon_validation(request, coupon_obj, cart_object, order_obj)  
                    else:
                        UserCoupon.objects.create(user=request.user, coupon=coupon_obj)
                        Coupon_validation(request, coupon_obj, cart_object, order_obj) 
                        
                else:
                    messages.warning(request, "Please enter valid coupon")
            else:
                messages.warning(request, "Please enter true coupon")
        return render(request, self.template_name, {"cart_count": cart, "cart_object": cart_object,"sub_total":sub_total, "total_discount":total_discount, "cates":cates})


class DeleteCrudUser(View):
    def get(self, request):
        id1 = request.GET.get('id', None)
        CartItem.objects.get(id=id1).delete()
        cart_item_obj = CartItem.objects.all()
        cart_total = 0
        for ca in cart_item_obj:
            cart_total += ca.sub_total
        car = Cart.objects.get(user=request.user)
        
        if car.total_discount:
            if car.total_discount >= cart_total:
                car.coupon = None
                car.total_discount = None
                car.save()
        car.total = car.get_total()
        car.save()
        if car.coupon:
            coupon_obj =car.coupon
            if coupon_obj.discount_type == "P":
                dis = (coupon_obj.discount / 10)
                total_discount = round((cart_total / 10) * int(dis))
                if total_discount > coupon_obj.max_discount:
                    total_discount = coupon_obj.max_discount
                car.coupon = coupon_obj
                car.total_discount = total_discount
                car.save()
        data = {
            'id': id1,
            "cart_item": len(cart_item_obj),
            "cart_sub_total": cart_total,
            "cart_total":car.total,
            "my_tag": "hidden",
            "cart_discount":car.total_discount
        }
        return JsonResponse(data)
      

class ShippingAddress(View):
    def get(self, request):
        address_object = Address.objects.filter(user=self.request.user)
        ship_addr_obj = address_object.filter(address_type="S")
        cates = Categorys.objects.all()
        cart_count = CartItem.objects.all()
        cart = Cart.objects.get(user=request.user)
        form = AddressForm()
        full_ship_ads = request.GET.get("shipping_address")
        if full_ship_ads:
            order_obj = Order.objects.filter(user=request.user)
            if order_obj:
                update_shipp = order_obj.get(user=request.user)
                update_shipp.shipping_address = Address.objects.get(id=int(full_ship_ads))
                update_shipp.save()
            else:
                Order.objects.create(user = request.user, shipping_address = Address.objects.get(id=int(full_ship_ads)))
                
            cart.shipping_address = Address.objects.get(id = int(full_ship_ads))
            cart.save()
            messages.success(request, "Your Shipping Address Successfully Added")
            return redirect("billing_address")
        return render(request, "shipping_address.html", {'form': form, "cates": cates, "cart_count": cart_count, "cart": cart, "ship_addr_obj": ship_addr_obj})

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
        cates = Categorys.objects.all()
        cart_count = CartItem.objects.all()
        cart = Cart.objects.get(user=request.user)
        messages.success(request, "Your New Shipping address create successfully")
        return render(request, "shipping_address.html", {'form': form, "cates": cates, "cart_count": cart_count, "cart": cart, "ship_addr_obj": ship_addr_obj})    

        
class BillingAddress(View):
    def get(self, request):
        address_object = Address.objects.filter(user=self.request.user)
        billing_addr_obj = address_object.filter(address_type="B")
        form = AddressForm()
        cates = Categorys.objects.all()
        cart_count = CartItem.objects.all()
        cart = Cart.objects.get(user=request.user)
        if cart.shipping_address == None:
            return redirect("shipping_address")
        full_bill_ads = request.GET.get("billing_address")
        if full_bill_ads:
            order_obj = Order.objects.filter(user=request.user)
            if order_obj:
                update_shipp = order_obj.get(user=request.user)
                update_shipp.billing_address = Address.objects.get(id=int(full_bill_ads))
                update_shipp.save()
            else:
                Order.objects.create(user=request.user, billing_address=Address.objects.get(id=int(full_bill_ads)))
                
            cart.billing_address = Address.objects.get(id = int(full_bill_ads))
            cart.save()
            messages.success(request, "Your Billing Address Successfully Added")
            return redirect("payment")
        return render(request, "billing_address.html", {'form': form, "cates": cates, "cart_count": cart_count, "cart": cart, "billing_addr_obj": billing_addr_obj})

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
        cates = Categorys.objects.all()
        cart_count = CartItem.objects.all()
        cart = Cart.objects.get(user=request.user)
        messages.success(request, "Your New Billing address create successfully")
        return render(request, "billing_address.html", {'form': form, "cates": cates, "cart_count": cart_count, "cart": cart, "billing_addr_obj": billing_addr_obj})   

class PaymentMethod(View):
    def get(self, request):
        cates = Categorys.objects.all()
        pay_option = PaymentOption.objects.all()
        cart_count = CartItem.objects.all()
        cart = Cart.objects.get(user=request.user)
        if cart.billing_address == None:
            return redirect("shipping_address")
        return render(request, "payment_option.html", {"cates": cates, "cart_count": cart_count, "cart": cart, "pay_option": pay_option})
        
        
class RemoveCode(View):
    def get(self, request, pk):
        cart_obj = Cart.objects.get(id=pk)
        cart_obj.coupon = None
        cart_obj.total_discount = None
        cart_obj.save()

        ord_obj = Order.objects.get(user=request.user)
        ord_obj.coupon = None
        ord_obj.total_discount = None
        ord_obj.save()

        return redirect("cartlists")