
from django.shortcuts import render,redirect,HttpResponse
from django.views import View       # This is for class base view
from .models import Customer,Product,Cart,OrderPlaced
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, request
from django.contrib.auth.decorators import login_required  #This is for fun base
from django.utils.decorators import method_decorator    # This is for class base

#Home view using class base view
class ProductView(View):
    def get(self,request):
        totalitem = 0
        
        bottomwear = Product.objects.filter(catogory='BW')
                       
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request,'app/home.html',{'bottomwear':bottomwear,'totalitem':totalitem})
        

#class base view for productDetailView
class ProductDetailView(View):
    def get(self,request,pk):
        totalitem = 0
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request,'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart,'totalitem':totalitem})

@login_required
def add_to_cart(request):
    totalitem = 0
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return redirect('/cart',{'totalitem':totalitem})

@login_required
def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user==user]
        #print(cart_product)
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discount_price)
                amount += tempamount
                totalamount = amount + shipping_amount
            return render(request,'app/addtocart.html',{'carts':cart,'totalamount':totalamount,'amount':amount,'totalitem':totalitem})
        else:
            return render(request,'app/emptycart.html')

#This function for plus cart
def plus_cart(request):  # sourcery skip: last-if-guard, move-assign-in-block
    if request.method =="GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user==request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discount_price)
            amount += tempamount
           

        data = {
            'quantity':c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)

# This Function for minus cart button
def minus_cart(request):
    if request.method =="GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user==request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discount_price)
            amount += tempamount

        data = {
            'quantity':c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)

# This Function for remove cart button

def remove_cart(request):
    if request.method =="GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user==request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discount_price)
            amount += tempamount

        data = {
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)

@login_required
def buy_now(request):
 return render(request, 'app/buynow.html')


@login_required
def address(request):
    totalitem = 0
    add = Customer.objects.filter(user=request.user)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/address.html',{'add':add,'active':'btn-primary','totalitem':totalitem})

#oder view for show placed order to user
@login_required
def orders(request):
    totalitem = 0
    op = OrderPlaced.objects.filter(user=request.user)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/orders.html',{'order_placed':op,'totalitem':totalitem})


    

#fun base view for bottom wear
def bottomwear(request,data=None):
    totalitem = 0
    if data ==None:
        bottom = Product.objects.filter(catogory='BW')
    elif data =='Lee' or data=='spyker':
        bottom = Product.objects.filter(catogory='BW').filter(brand=data)
    elif data =='below':
        bottom = Product.objects.filter(catogory='BW').filter(discount_price__lt=500)
    elif data =='above':
        bottom = Product.objects.filter(catogory='BW').filter(discount_price__gt=500)
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request,'app/bottomwear.html',{'bottom':bottom,'totalitem':totalitem})

#login 
#using deafult djangoform LoginView(form) direct used in urls.py

#passwordChange
#using deafult djangoform PasswordChangeView(form) direct used in urls.py

#passwordReset
#using deafult djangoform PasswordResetView,PasswordResetDoneView,PasswordResetConfirmView,PasswordResetCompleteView direct used in urls.py


#registration form class base view
class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request,'app/customerregistration.html',{'form':form})
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'congratulations..! Registered Successfully')
            form.save()
        return render(request,'app/customerregistration.html',{'form':form})


@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user==request.user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discount_price)
            amount +=tempamount
            totalamount = amount + shipping_amount
    return render(request, 'app/checkout.html',{'add':add,'totalamount':totalamount,'cart_items':cart_items})

#paymentdone View
@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)

    for c in cart:
        OrderPlaced(user=user,customer=customer,product= c.product,quantity=c.quantity).save()
        c.delete()
    return redirect("orders")



# profile View
@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        totalitem = 0
        form = CustomerProfileForm()
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary','totalitem':totalitem})
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr =request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'Congratulations.!! Profile Updated Successfully')
        return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})

#Session



#Time 7:4:30  