from .models import Categorys, Cart, CartItem

def add_variable_to_context(request):
    cart_object = Cart.objects.get(user=request.user)
    total_cart_item = cart_object.cart_item.all()
    return {
        'cart_item_count': total_cart_item,
        "categorys":Categorys.objects.all(),
    }