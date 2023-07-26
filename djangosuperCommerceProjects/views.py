from __future__ import unicode_literals
from django_daraja.mpesa import utils
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django_daraja.mpesa.core import MpesaClient
from decouple import config
from datetime import datetime

from django.shortcuts import render, redirect
from.models import Products
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'index.html')

@login_required

def add_product(request):
    if request.method == "POST" :
        prod_name = request.POST.get("p-name")
        prod_qtty = request.POST.get("p-qtty")
        prod_size = request.POST.get("p-size")
        prod_price = request.POST.get("p-price")

        context = {
            "prod_name": prod_name,
            "prod_qtty": prod_qtty,
            "prod_size": prod_size,
            "prod_price": prod_price,
            "success": "Product saved successfully"
        }

        query = Products(name=prod_name,qtty=prod_qtty,
                        size=prod_size,price=prod_price)
        query.save()
        return render(request, 'add-product.html', context)

    return render(request, 'add-product.html')

@login_required
def all_products(request):
    products = Products.objects.all()
    context = {"products": products}
    return render(request, 'products.html', context)

@login_required
def delete_product(request, id):
    product = Products.objects.get(id=id)
    product.delete()
    messages.success(request, 'Products deleted successfully')
    return redirect('all-products')


@login_required
def update_product(request, id):
    product = Products.objects.get(id=id)
    context = {"product": product}
    if request.method == 'POST':
        update_name = request.POST.get('p-name')
        update_qtty = request.POST.get('p-qtty')
        update_size = request.POST.get('p-size')
        update_price = request.POST.get('p-price')
        product.name = update_name
        product.qtty = update_qtty
        product.size= update_size
        product.price = update_price
        product.save()
        messages.success(request,'Product updated successfully')
    return render(request, 'update-product.html', context)


def register(request):
    if request.method == "POST":
        form =UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User registered successfully")
            return redirect ('user-registration')
    else:
        form =UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


def shop(request):
    products = Products.objects.all()
    context = {"products": products}
    return render(request, 'shop.html', context)

mpesa_client = MpesaClient()
stk_push_callback_url = 'https://api.darajambili.com/express-payment'


def auth_success(request):
    response = mpesa_client.access_token()
    return JsonResponse(response, safe=False)

def pay(request,id):
    product = Products.objects.get(id=id)
    context = {"product": product}
    if request.method == "POST":
        phone_number = request.POST.get('c-phone')
        product_price = request.POST.get('p-price')
        product_price = int(product_price)
        receipt_number = "PAYMENT_1"
        transaction_desc = "Paying for a product"
        transaction = mpesa_client.stk_push(phone_number, product_price,
                                            receipt_number, transaction_desc,
                                            stk_push_callback_url)
        return JsonResponse(transaction.response_description, safe=False)
    return render(request, 'pay.html', context)
