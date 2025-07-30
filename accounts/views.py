from django.dispatch import receiver
from django.http import HttpResponseRedirect , HttpResponse
from django.shortcuts import render , redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from .models import Profile
from django.db.models.signals import post_save
from products.models import Coupon, Product , SizeVariant
from .models import Cart , CartItems
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

# Create your views here.
def login_page(request):

    if request.method == 'POST' :
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if not user_obj.exists():
            messages.warning(request, "Account not found.")
            return HttpResponseRedirect(request.path_info)
        
        user = user_obj.first()
        
        if not user.profile.is_email_verified:
            messages.warning(request, "Your account is not verified.")
            return HttpResponseRedirect(request.path_info)
        
        user_obj = authenticate(username = email , password = password)
        if user_obj:
            login(request , user_obj)
            # print(request.user.profile.get_cart_count())
            return redirect('/')

        messages.warning(request, "Invaild Credentials.")
        return HttpResponseRedirect(request.path_info)

    return render(request , 'accounts/login.html')

def register_page(request):

    if request.method == 'POST' :
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = email)

        if user_obj.exists():
            messages.warning(request, "Email is already taken.")
            return HttpResponseRedirect(request.path_info)
        

        user_obj = User.objects.create(first_name = first_name , last_name = last_name , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()

        messages.success(request, "An Email has been sent on your mail.")
        return HttpResponseRedirect(request.path_info)



    return render(request , 'accounts/register.html')


def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token = email_token)
        user.is_email_verified = True
        user.save()
        return render(request, 'base/verifyAlert.html')
    except Exception as e:
        return HttpResponse("Invalid Email token.")
    
@login_required(login_url='/accounts/login/')
def add_to_cart(request , uid):
    variant = request.GET.get('variant')
    product = Product.objects.get(uid = uid)
    user = request.user
    cart , _ = Cart.objects.get_or_create(user = user , is_paid = False)
    
    cart_item = CartItems.objects.create(cart = cart , product = product)
    # print(cart_item)

    if variant :
        variant = request.GET.get('variant')
        size_variant = SizeVariant.objects.get(size_name = variant)
        cart_item.size_variant = size_variant
        cart_item.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_cart_item(request , cart_item_uid):
    try:
        cart_item = CartItems.objects.get(uid = cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))





def cart(request):
    # cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    # cart_items = cart.cart_items.all() if cart else []
    
    # cart_total = sum(item.get_product_price() for item in cart_items) # Calculate total price
    # # cart_total = cart.get_cart_total() if cart else 0 # Get total price from Cart model method

    if not request.user.is_authenticated:
        messages.info(request, "Please register or sign in to view your cart.")
        return redirect('/accounts/login')  # or wherever your login URL is named


    cart = Cart.objects.get(user = request.user)
    cart_items = cart.cart_items.all()
    cart_total = cart.get_cart_total()

    if request.method == 'POST':
        coupon = request.POST.get('coupon' , '').strip()
        coupon_obj = Coupon.objects.filter(coupon_code__iexact = coupon)
        if not coupon_obj.exists():
            messages.warning(request, "Invalid Coupon.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        # if cart.coupon:
        #     messages.warning(request, "Coupon already applied.")
        #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_total < coupon_obj.first().minimum_amount:
            messages.warning(request , f'Amount should be greater than {coupon_obj.first().minimum_amount}.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if coupon_obj.first().is_expired:
            messages.warning(request , 'Coupon expired.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
        
        cart.coupon = coupon_obj.first()
        cart.save()

        cart_total = cart_total - coupon_obj.first().discount_price
        print(coupon_obj.first().discount_price , cart_total)
        messages.success(request, "Coupon applied successfully.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    
    

    # context = {
    #     'cart_items': cart_items,
    #     'cart_total': cart_total  # Send total price to the template
    # }
    

    # for item in cart_items:
    #     print(item.product.product_name, item.quantity)

    # print(cart.get_cart_total())
    cart_total = cart_total - (cart.coupon.discount_price if cart.coupon else 0)
    print(cart_total)
    context = {
        'cart_items' : cart_items,
        'cart_total' : cart_total,
        'cart' : cart,
    } 
    print(cart_total)
    
    return render(request , 'accounts/cart.html', context) 

@require_POST
def remove_coupon(request):
    try:
        cart = Cart.objects.get(user=request.user, is_paid=False)
        if cart.coupon:
            cart.coupon = None
            cart.save()
            messages.success(request, "Coupon removed successfully.")
        else:
            messages.info(request, "No coupon was applied.")
    except Cart.DoesNotExist:
        messages.error(request, "Cart not found.")
    
    return redirect('cart')

def logout_page(request):
    logout(request)
    return redirect('/')

