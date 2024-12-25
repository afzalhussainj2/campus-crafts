from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from GrillGuard.utils import sending_mail, otp_generator, generate_unique_bill_number
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from .models import User, Product, Waiter, Order, Bill, Complain
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


    

def user_login(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Use authenticate to check the credentials
        user = get_user_model().objects.get(email=email)
        if user is not None:
            if user.check_password(password):
                user.backend = 'GrillGuard.backends.EmailBackend'
                login(request, user)  # Log the user in
            # Redirect based on user type
                if user.is_student:
                    return redirect('dashboard_student')
                elif user.is_seller:
                    return redirect('dashboard_seller')
                elif user.is_admin:
                    return redirect('dashboard_admin')
            else:
                messages.error(request, 'Invalid credentials or user does not exist')

    return render(request, 'login.html')

def user_signup(request):
    User = get_user_model()
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        name = request.POST.get('name')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered')
            return redirect('register')
        
        try:
            current_user = User.objects.create_user(
                email=email,
                password=password
                )
            current_user.name = name
            current_user.is_student = True

            current_user.save()

            current_user.backend = 'GrillGuard.backends.EmailBackend'
            login(request, current_user)
            return redirect('dashboard_student')
        except Exception as e:
            import traceback
            traceback.print_exc() 
            messages.error(request, 'Error creating user')
            return redirect('register')
    get_token(request)
    return render(request, 'sign_up.html')

def logout_user(request):
    logout(request)
    return redirect('login_page')

def email_verification_password_reset(request):

    User = get_user_model()
    if request.method == 'POST':
        email = request.POST.get('email')

        if not User.objects.filter(email=email).exists():
            messages.error(request, 'User does not exist')
            return redirect('resetemail')
        
        otp = otp_generator()
        request.session['otp'] = int(otp)
        request.session['email'] = email
        sending_mail(email, otp)
        messages.success(request, 'Email sent')
        return redirect('resetotp')
    
    return render(request, 'reset1.html')

def otp_verification_password_reset(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if int(otp) == int(request.session['otp']):
            del request.session['otp']
            return redirect('resetpass')
        else:
            messages.error(request, 'Invalid OTP')
            return redirect('otp')
    return render(request, 'reset2.html')

def save_pass_password_reset(request):
    User = get_user_model()
    if request.method == 'POST':
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')
        email = request.session['email']

        if not email:
            messages.error(request, 'Session expired. Please restart the process.')
            return redirect('resetemail')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('savepass')
        
        current_user = User.objects.get(email=email)
        current_user.set_password(password1)
        current_user.save()
        messages.success(request, 'Password reset successful')
        del request.session['email']
        return redirect('login_page')
        
    return render(request,'reset1.html')

def reset_otp_page(request):
    return render(request, 'reset2.html')

def reset_email_page(request):
    return render(request, 'reset1.html')

def reset_password_page(request):
    return render(request, 'reset3.html')

def register_page(request):
    return render(request, 'sign_up.html')

def login_page(request):
    return render(request, 'login.html')

@login_required
def student_dashboard(request):
    bills = Bill.objects.all()  # QuerySet of bills
    orders = Order.objects.all()  # QuerySet of orders
    producs = Product.objects.all()
    waiters = Waiter.objects.all()  # QuerySet of waiters
    
    bills_data = list(bills.values('table', 'waiter__name', 'total', 'bill_number'))
    orders_data = list(orders.values('product__name', 'quantity', 'bill__bill_number'))
    products_data = list(producs.values('name', 'price'))
    waiters_data = list(waiters.values('name', 'tables'))

    bills_json = json.dumps(bills_data)
    orders_json = json.dumps(orders_data)
    products_json = json.dumps(products_data)
    waiters_json = json.dumps(waiters_data)

    context = {
        'user': request.user,
        'products': producs,
        'products_json': products_json,
        'bills': bills,
        'bills_json': bills_json,
        'orders': orders,
        'orders_json': orders_json,
        'waiters': waiters_data,
        'waiters_json': waiters_json
    }
    return render(request, 'dashboard_student.html', context)

@login_required
def seller_dashboard(request):

    waiters = Waiter.objects.all()  # QuerySet of waiters
    bills = Bill.objects.all()  # QuerySet of bills
    orders = Order.objects.all()  # QuerySet of orders
    producs = Product.objects.all()
    
    waiters_data = list(waiters.values('name', 'tables'))
    bills_data = list(bills.values('table', 'waiter', 'total', 'bill_number'))
    orders_data = list(orders.values('product__name', 'quantity', 'bill__bill_number'))
    products_data = list(producs.values('name', 'price'))

    waiter_json = json.dumps(waiters_data)
    bills_json = json.dumps(bills_data)
    orders_json = json.dumps(orders_data)
    products_json = json.dumps(products_data)
    context = {
        'user': request.user,
        'products': producs,
        'products_json': products_json,
        'waiters': waiters_data,
        'waiter_json': waiter_json,
        'bills': bills,
        'bills_json': bills_json,
        'orders': orders,
        'orders_json': orders_json
    }
    return render(request, 'dashboard_seller.html', context)

@login_required
def admin_dashboard(request):
    bills = Bill.objects.all()  # QuerySet of bills
    orders = Order.objects.all()  # QuerySet of orders
    producs = Product.objects.all()
    waiters = Waiter.objects.all()  # QuerySet of waiters
    
    bills_data = list(bills.values('table', 'waiter', 'total', 'bill_number'))
    orders_data = list(orders.values('product__name', 'quantity', 'bill__bill_number'))
    products_data = list(producs.values('name', 'price'))
    waiters_data = list(waiters.values('name', 'tables'))

    bills_json = json.dumps(bills_data)
    orders_json = json.dumps(orders_data)
    products_json = json.dumps(products_data)
    waiters_json = json.dumps(waiters_data)

    context = {
        'user': request.user,
        'products': producs,
        'products_json': products_json,
        'bills': bills,
        'bills_json': bills_json,
        'orders': orders,
        'orders_json': orders_json,
        'waiters': waiters_data,
        'waiters_json': waiters_json
    }
    return render(request, 'dashboard_admin.html', context)

def complain_seller(request):
    complains = request.user.complaints_against_seller.all()
    total_complains = complains.count()
    approved_complains = complains.filter(status='Approved').count()

    context = {
        'complains': complains,
        'total_complains': total_complains,
        'approved_complains': approved_complains,
        'user': request.user,
        'sellers': User.objects.filter(is_seller=True)
    }

    return render(request, 'complain_seller.html', context)

def complain_student(request):
    sellers = User.objects.filter(is_seller=True)
    complains = Complain.objects.filter(froom=request.user)
    total_complains = complains.count()
    approved_complains = complains.filter(status='Approved').count()

    context = {
        'sellers': sellers,
        'user': request.user,
        'complains': complains,
        'total_complains': total_complains,
        'approved_complains': approved_complains
    }

    return render(request, 'complain_student.html', context)

def complain_admin(request):
    total_complains = Complain.objects.all().count()
    complains = Complain.objects.all()
    approved_complains = Complain.objects.filter(status='Approved').count()

    context = {
        'complains': complains,
        'total_complains': total_complains,
        'approved_complains': approved_complains,
        'user': request.user,
        'sellers': User.objects.filter(is_seller=True)
    }

    return render(request, 'complain_admin.html', context)

def waitermanagement(request):
    waiters = Waiter.objects.all()
    waiter_data = list(waiters.values('name', 'tables', 'phone'))
    waiter_json = json.dumps(waiter_data)

    context = {
        'waiters': waiters,
        'waiter_json': waiter_json
    }

    return render(request, 'waiters.html', context)

def sellermanagement(request):
    seller = User.objects.filter(is_seller=True)
    seller_data = list(seller.values('name', 'phone', 'email', 'is_active'))


    seller_json = json.dumps(seller_data)

    context = {
        'sellers': seller,
        'seller_json': seller_json
    }

    return render(request, 'sellers.html', context)

@csrf_exempt
def save_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_name = data.get('product')
            quantity = data.get('quantity')
            waiter_name = data.get('waiter')
            table_number = data.get('table')
            total_price = data.get('total_price')

            # Check if Bill exists for the given table and waiter
            exists = Bill.objects.filter(table=table_number, waiter__name=waiter_name).exists()
            
            if exists:
                # Retrieve the existing Bill
                bill = Bill.objects.get(table=table_number, waiter__name=waiter_name)
            else:
                # Generate a unique bill number
                bill_number = generate_unique_bill_number()
                
                # Create a new Bill
                waiter = Waiter.objects.get(name=waiter_name)  # Fetch waiter instance
                bill = Bill.objects.create(
                    table=table_number,
                    total=total_price,
                    waiter=waiter,
                    bill_number=bill_number
                )
            
            # Fetch the product instance
            product = Product.objects.get(name=product_name)
            
            # Create an Order associated with the Bill
            Order.objects.create(
                product=product,
                bill=bill,
                quantity=quantity
            )
            
            # Update the total on the Bill
            if exists:
                bill.total += total_price
                bill.save()
            
            return JsonResponse({'success': True, 'message': 'Order saved successfully!'})

        except Waiter.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Waiter not found.'})
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt
def save_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_name = data.get('product')
            product_price = data.get('price')

            # Check if Bill exists for the given table and waiter
            exists = Product.objects.filter(name=product_name).exists()
            
            if exists:
                return JsonResponse({'success': False, 'message': 'Product already exists.'})                
            else:                
                product = Product.objects.create(
                    name=product_name,
                    price=product_price
                )
                return JsonResponse({'success': True, 'message': 'Order saved successfully!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@csrf_exempt
def remove_seller(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        seller_email = data.get('email')
        
        # Validate the input
        if not seller_email:
            return JsonResponse({'error': 'Invalid input'}, status=400)

        curren_seller = User.objects.get(email=seller_email)    
        curren_seller.delete()

        return JsonResponse({'success': True, 'message': 'Seller added successfully!'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def remove_waiter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        waiter_name = data.get('name')
        
        # Validate the input
        if not waiter_name:
            return JsonResponse({'error': 'Invalid input'}, status=400)

        curren_waiter = Waiter.objects.get(name=waiter_name)    
        curren_waiter.delete()

        return JsonResponse({'success': True, 'message': 'Waiter added successfully!'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def save_seller(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            seller_name = data.get('name')
            seller_phone = data.get('phone')
            seller_email = data.get('email')
            seller_password = data.get('password')

            # Validate the input
            if not seller_name or not seller_phone or not seller_email or not seller_password:
                return JsonResponse({'error': 'Invalid input'}, status=400)

            # Check if the waiter already exists
            try:
                current_seller = User.objects.get(email=seller_email)
                return JsonResponse({'error': 'Waiter already exists with equal or higher table count.'}, status=400)
            except User.DoesNotExist:
                # Create a new waiter if not found
                User.objects.create(
                    name=seller_name,
                    phone=seller_phone,
                    email=seller_email,
                    password=seller_password,
                    is_seller=True
                )
                return JsonResponse({'success': True, 'message': 'Waiter added successfully!'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def save_waiter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            waiter_name = data.get('name')
            waiter_phone = data.get('phone')
            waiter_tables = data.get('tables')

            # Validate the input
            if not waiter_name or not waiter_phone or not isinstance(waiter_tables, int):
                return JsonResponse({'error': 'Invalid input'}, status=400)

            # Check if the waiter already exists
            try:
                current_waiter = Waiter.objects.get(name=waiter_name)
                # Update tables if the new value is greater
                if current_waiter.tables < waiter_tables:
                    current_waiter.tables = waiter_tables
                    current_waiter.save()
                    return JsonResponse({'success': True, 'message': 'Waiter updated successfully!'})
                else:
                    return JsonResponse({'error': 'Waiter already exists with equal or higher table count.'}, status=400)
            except Waiter.DoesNotExist:
                # Create a new waiter if not found
                Waiter.objects.create(
                    name=waiter_name,
                    phone=waiter_phone,
                    tables=waiter_tables,
                )
                return JsonResponse({'success': True, 'message': 'Waiter added successfully!'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def save_complain(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        seller_name = data.get('seller')
        complaint_text = data.get('complaint')
        user_student = request.user

        # Validate the input
        if not seller_name or not complaint_text or not user_student:
            return JsonResponse({'error': 'Invalid input'}, status=400)

        # Get the seller object
        seller = get_object_or_404(User, name=seller_name, is_seller=True)
        student = get_object_or_404(User, name=user_student, is_student=True)
        
        # Save the complaint
        Complain.objects.create(
            against=seller,
            froom=student,
            complain=complaint_text,
        )

        return JsonResponse({'message': 'Complaint submitted successfully!'})

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def update_complain_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            complaint_id = data.get('complaint_id')
            new_status = data.get('new_status')

            # Update the complaint in the database
            from .models import Complain
            complaint = Complain.objects.get(id=complaint_id)
            complaint.status = new_status
            complaint.save()

            return JsonResponse({'success': True, 'message': 'Status updated successfully'})
        except Complain.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Complaint not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)