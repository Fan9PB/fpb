from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Customer, Product, Order, UserExtension
from .forms import CustomerForm, OrderForm, RegisterForm


# Create your views here.

@login_required(login_url='login')
# admin:FPB password:1234
def homepage(request):
    customer = Customer.objects.all()
    c_cunt = customer.count()
    order_p_count = Order.objects.filter(status='Pending').count()
    order_d_count = Order.objects.filter(status='Delivered').count()
    order_o_count = Order.objects.filter(status='Out for delivery').count()
    order = Order.objects.all()
    o_count = order.count()
    c = 0
    last_ten = []
    for i in reversed(order):
        if c < 10:
            last_ten.append(i)
            c += 1
        else:
            break

    if request.is_ajax and request.POST.get('order_del'):
        del_order_id = request.POST.get('order_del')
        del_order = Order.objects.get(id=del_order_id)
        del_order.delete()

    context = {
        'customer': customer,
        'c_count': c_cunt,
        'last_ten': last_ten,
        'order_p_count': order_p_count,
        'order_d_count': order_d_count,
        'order_o_count': order_o_count,
        'o_count': o_count

    }
    return render(request, 'fpbapp/home.html', context)


def register(request):
    r_form = RegisterForm()
    message1 = ''
    message = ''

    if request.method == 'POST':
        r_form = RegisterForm(request.POST)
        if r_form.is_valid():
            name_get = r_form.cleaned_data['username']
            pw1_get = r_form.cleaned_data['password1']
            pw2_get = r_form.cleaned_data['password2']
            email_get = r_form.cleaned_data['email']
            phone_get = r_form.cleaned_data['phone']

            try:
                if pw1_get == pw2_get:
                    new_user = User.objects.create_user(username=name_get, password=pw1_get, email=email_get)
                    new_user.save()
                    UserExtension.objects.create(user=new_user, phone=phone_get).save()
                    message1 = '注册成功'
                    return redirect('login')
                else:
                    message = '两次密码输入不一致！'
            except:
                message = '用户名或邮箱已经被注册！'

    context = {
        'r_form': r_form,
        'message': message,
        'message1': message1
    }
    return render(request, 'fpbapp/register.html', context)


def login_page(request):
    message = ''

    if request.user.is_authenticated:
        return redirect('homepage')
    else:
        if request.method == 'POST':
            name_get = request.POST.get('username')
            pwd_get = request.POST.get('password')
            user = authenticate(request, username=name_get, password=pwd_get)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('homepage')
                else:
                    message = '此账号已被冻结！'
            else:
                message = '用户名或密码错误！'

    context = {
        'message': message
    }
    return render(request, 'fpbapp/loginpage.html', context)


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def modify_pwd(request):
    message = ''

    if request.method == 'POST':
        old_pwd = request.POST.get('old_pwd')
        new_pwd = request.POST.get('new_pwd')
        repeat_pwd = request.POST.get('repeat_pwd')
        user = authenticate(request, username=request.user.username, password=old_pwd)
        if user is not None:
            if user.is_active:
                if new_pwd != repeat_pwd:
                    message = '两次输入的密码不一致！'
                else:
                    user.set_password(new_pwd)
                    user.save()
                    logout(request)
                    return redirect('login')
            else:
                message = '此账号已被冻结！'
        else:
            message = '原密码输入错误，或用户不存在！'

    context = {
        'message': message
    }
    return render(request, 'fpbapp/modifypwd.html', context)


@login_required(login_url='login')
def create(request):
    c_form = CustomerForm()
    o_form = OrderForm()

    if request.method == 'POST':
        if 'o-button' in request.POST:
            o_form = OrderForm(request.POST)
            if o_form.is_valid():
                customer_get = o_form.cleaned_data['customer']
                product_get = o_form.cleaned_data['product']
                status_get = o_form.cleaned_data['status']
                order = Order.objects.create(customer=customer_get, product=product_get, status=status_get)
                order.save()
                return redirect('homepage')

        if 'c-button' in request.POST:
            c_form = CustomerForm(request.POST)
            if c_form.is_valid():
                name_get = c_form.cleaned_data['name']
                phone_get = c_form.cleaned_data['phone']
                email_get = c_form.cleaned_data['email']
                customer = Customer.objects.create(name=name_get, phone=phone_get, email=email_get)
                customer.save()
                return redirect('homepage')

    context = {
        'c_form': c_form,
        'o_form': o_form
    }
    return render(request, 'fpbapp/create.html', context)


@login_required(login_url='login')
def update_order(request, pk):
    order = Order.objects.get(id=pk)
    o_form = OrderForm(instance=order)

    if request.method == 'POST':
        o_form = OrderForm(request.POST)
        if o_form.is_valid():
            customer_get = o_form.cleaned_data['customer']
            product_get = o_form.cleaned_data['product']
            status_get = o_form.cleaned_data['status']
            order = Order.objects.filter(id=pk)
            order.update(id=pk, customer=customer_get, product=product_get, status=status_get)
            return redirect('homepage')

    context = {
        'order': order,
        'o_form': o_form
    }
    return render(request, 'fpbapp/updateorder.html', context)


@login_required(login_url='login')
def delete_order(request, pk):
    order = Order.objects.get(id=pk)

    if request.method == 'POST':
        order.delete()
        return redirect('homepage')

    context = {
        'order': order,
    }
    return render(request, 'fpbapp/deleteorder.html', context)
