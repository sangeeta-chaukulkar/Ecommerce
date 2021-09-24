from django.shortcuts import render,redirect
from django.views import View
from .models import (Customer,Product,Cart,OrderPlaced)
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
#def home(request):
# return render(request, 'core/home.html')
class ProductView(View):
    def get(self,request):
        topwears=Product.objects.filter(catehory='TW')
        bottomwears=Product.objects.filter(catehory='BW')
        mobiles=Product.objects.filter(catehory='M')
        laptops=Product.objects.filter(catehory='L')
        return render(request, 'core/home.html',{'topwears':topwears,'bottomwears':bottomwears,'mobiles':mobiles,'laptops':laptops})
#def product_detail(request):
# return render(request, 'core/productdetail.html')

class ProductDetailView(View):
    def get(self,request,pk):
        product=Product.objects.get(pk=pk)
        item_already_in_cart=False
        if request.user.is_authenticated:
            item_already_in_cart=Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request, 'core/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart})
        
@login_required
def add_to_cart(request):
    user=request.user 
    product_id=request.GET.get('prod_id')
    print(product_id)
    product=Product.objects.get(id=product_id) 
    print(product)
    carts=Cart(user=user,product=product)
    carts.save()
    print(carts)
    return redirect('/cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user=request.user
        cart=Cart.objects.filter(user = user)
        amount=0.0
        shipping_amount=70.0
        total_amount=0.0
        cart_product=[p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamount=(p.quantity * p.product.discounted_price)
                amount += tempamount
            total_amount= amount +shipping_amount
            return render(request,'core/addtocart.html',{'carts':cart,'totalamount':total_amount,'amount':amount})
        else:
            return render(request,'core/emptycart.html')
        
def plus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET.get('prod_id')
        print(request.user)
        print(prod_id)
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount=0.0
        shipping_amount=70.0
        cart_product=[p for p in Cart.objects.all() if p.user==request.user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount += tempamount
            #total_amount= amount +shipping_amount
        data={
            'quantity':c.quantity,
                'amount':amount,
                'total_amount':amount + shipping_amount
            }
        return JsonResponse(data)

def minus_cart(request):
    if request.method== 'GET':
        prod_id=request.GET.get('prod_id')
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        amount=0.0
        shipping_amount=70.0
        cart_product=[p for p in Cart.objects.all() if p.user==request.user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount += tempamount
            #total_amount= amount +shipping_amount
        data={
            'quantity':c.quantity,
                'amount':amount,
                'total_amount':amount +shipping_amount
            }
        return JsonResponse(data)

def remove_cart(request):
    if request.method== 'GET':
        prod_id=request.GET.get('prod_id')
        c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount=0.0
        shipping_amount=70.0
        cart_product=[p for p in Cart.objects.all() if p.user==request.user]
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount += tempamount
        data={
                'amount':amount,
                'total_amount':amount +shipping_amount
            }
        return JsonResponse(data)


def buy_now(request):
 return render(request, 'core/buynow.html')

def profile(request):
 return render(request, 'core/profile.html')

@login_required
def address(request):
    add=Customer.objects.filter(user=request.user)
    return render(request, 'core/address.html',{'add':add,'active':'btn-primary'})

@login_required
def orders(request):
    op=OrderPlaced.objects.filter(user=request.user)
    return render(request, 'core/orders.html',{'order_placed':op})

def change_password(request):
 return render(request, 'core/changepassword.html')

def mobile(request,data=None):
    if data == None:
        mobiles=Product.objects.filter(catehory='M')
    elif data== 'Redmi' or data =='samsung':
        mobiles=Product.objects.filter(catehory='M').filter(brand=data)
    elif data=='below':      
        mobiles=Product.objects.filter(catehory='M').filter(discounted_price__lt=15)
    elif data=='above':  
        mobiles=Product.objects.filter(catehory='M').filter(discounted_price__gt=15)   
    return render(request, 'core/mobile.html',{'mobiles': mobiles})

def laptop(request,data=None):
    if data == None:
        laptops=Product.objects.filter(catehory='L')
    elif data== 'Dell' or data =='hp' or data =='lenovo' :
        laptops=Product.objects.filter(catehory='L').filter(brand=data)
    elif data=='below':      
        laptops=Product.objects.filter(catehory='L').filter(discounted_price__lt=30)
    elif data=='above':  
        laptops=Product.objects.filter(catehory='L').filter(discounted_price__gt=30)   
    return render(request, 'core/laptop.html',{'laptops': laptops})

def login(request):
 return render(request, 'core/login.html')

#def customerregistration(request):
# return render(request, 'core/customerregistration.html')

class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegistrationForm()
        return render(request, 'core/customerregistration.html',{'form': form })
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'Congrats Registered successfully!')
            form.save()
        return render(request, 'core/customerregistration.html',{'form': form })

@login_required
def checkout(request):
    user=request.user
    add=Customer.objects.filter(user=user)
    cart_items=Cart.objects.filter(user=user)
    amount=0.0
    shipping_amount=70.0
    total_amount=0.0 
    cart_product=[p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            tempamount=(p.quantity * p.product.discounted_price)
            amount += tempamount
        total_amount= amount +shipping_amount   
    return render(request, 'core/checkout.html',{'add':add,'total_amount':total_amount,'cart_items':cart_items})

@login_required
def payment_done(request):
    user=request.user
    print(request.GET)
    custid=request.GET.get('custid')
    customer=Customer.objects.get(id=custid)
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
        c.delete()
    return redirect('orders') 

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form=CustomerProfileForm()
        return render(request,'core/profile.html',{'form':form,'active':'btn-primary'})
    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            usr=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            state=form.cleaned_data['state']
            zipcode=form.cleaned_data['zipcode']
            reg=Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'Congrats profile updated successfully')
        return render(request,'core/profile.html',{'form':form,'active':'btn-primary'})