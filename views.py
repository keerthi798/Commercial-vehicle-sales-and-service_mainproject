from audioop import reverse
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .forms import WorkerForm
from django.http import JsonResponse
from allauth.socialaccount.models import SocialAccount,SocialApp
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import HttpResponse
from django.core.mail import send_mail
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login
# from .forms import ServiceBookingForm
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from .models import ServiceBooking
from .forms import PartForm
from .models import UserProfile  # Adjust the import from forms to models
from .models import Parts,CartItem,WishlistItem
from .models import CustomUser
import re
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.html import strip_tags
from .models import Cart,CartItem1
from django.http import JsonResponse
from django.conf import settings
from .models import UserProfile, Parts, Cart, CartItem1, Order, OrderItem
import razorpay
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from .forms import VehicleForm
from .models import Vehicle, VehicleImage
def index(request):
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            # ... (your logic here)
        except ObjectDoesNotExist:
            user_profile = None  # or handle as needed (create a profile, redirect, etc.)
    else:
        return render(request, 'index.html')

    return render(request, 'index.html', {'user_profile': user_profile})
    
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        address = request.POST['address']
        phone_number = request.POST['phone_number']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        role = request.POST['role'] 
        if not username:
            error_message = 'Username is required.'
            return render(request, 'signup.html', {'error_message': error_message})

        if not username[0].isupper():
            error_message = 'Username must start with a capital letter.'
            return render(request, 'signup.html', {'error_message': error_message})

        if not re.match(r'^[A-Z][a-zA-Z0-9]{0,9}$', username):
            error_message = 'Username can only contain uppercase letters followed by lowercase letters, characters, and numbers (maximum 10 characters).'
            return render(request, 'signup.html', {'error_message': error_message})

        if ' ' in username:
            error_message = 'Username cannot contain white spaces.'
            return render(request, 'signup.html', {'error_message':error_message})


        # Check if the email already exists in the database
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error_message': 'Email address is already in use.'})
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error_message': 'username is already in use.'})
        if password != confirm_password:
            return render(request, 'signup.html', {'error_message': 'Passwords do not match'})

        # Create a new user object
        user = CustomUser.objects.create_user(username=username,email=email, address=address, phone_number=phone_number,password=password, role=role)
        subject = 'Your Account Details'
        html_message = render_to_string('worker_info.html', {'username': username, 'password': password})
        plain_message = strip_tags(html_message)  # Strip HTML tags for plain text email
        from_email = 'ava.mi2001@gmail.com'  # Replace with your email
        to_email = email
        # Store user ID in the session
        send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

        messages.success(request, 'Registration successful. Account details have been sent to your email.')
        # Redirect to the dashboard after successful registration
        return redirect('login')

    return render(request, 'signup.html')
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)  # Log in the user
            request.session['user_id'] = user.id 

            if user.role == "service_center":
                return redirect("servicebranchdashboard")
            elif user.role == "user":
                return redirect("index")
            elif user.username == "keerthisree":
                return redirect("admindashboard")
            elif user.role == "parts_manager":
                return redirect("partsmanagerdashboard")          
        else:
            messages.error(request, "Incorrect username or password. Please try again.")

    return render(request, 'login.html')

def logout_confirm(request):
    if request.user.is_authenticated:
          # Remove your custom session data
        
        # Clear any Google-related session data if you have stored it
       
        logout(request)
    return render(request, 'logout_confirm.html')
def logout_view(request):
    logout(request)
    # Redirect to the homepage or any other desired page after logout
    return redirect('dashboard')


def dashboard(request):
    return render(request, 'index.html') 
#     Use session data to retrieve the user object
# # def booking(request):
#     if request.method == 'POST':
#         form = ServiceBookingForm(request.POST)
#         if form.is_valid():
#             # Assign the user directly to the form's user field
#             form.instance.user = request.user
#             form.save()
#             success_message = "Service booking has been successfully updated."
#             return render(request, 'index.html', {'success_message': success_message})

#     else:
#         form = ServiceBookingForm()
#     bookings = ServiceBooking.objects.all()  # Fetch existing bookings

#     return render(request, 'booking.html', {'form': form, 'bookings': bookings})
# @login_required
def booking(request):
    # if request.method == 'POST':
    #     form = ServiceBookingForm(request.POST)
    #     if form.is_valid():
    #         service_booking = form.save(commit=False)
    #         service_booking.user = request.user
    #         service_booking.save()
    #         success_message = "Service booking has been successfully updated."
    #         return render(request, 'index.html', {'success_message': success_message})
    # else:
    #     form = ServiceBookingForm()
    return render(request, 'booking.html')



def partsorder(request, category):
    user_profile = UserProfile.objects.get(user=request.user)
    parts_orders = Parts.objects.filter(categories=category)
    return render(request, 'partsorder.html', {'parts_orders': parts_orders, 'user_profile': user_profile})


   
def customer_dash(request):
    # Retrieve data or perform any necessary actions here
    # Example: data = YourModel.objects.all()

    return render(request, 'customer_dash.html')

def admindashboard(request):
    users = CustomUser.objects.all()
    user_count = users.count()
    
    return render(request, 'admindashboard.html', {'users': users, 'user_count': user_count})

       


def servicebranchdashboard(request):
    
    # Your view logic goes here
    return render(request, 'servicebranchdashboard.html')
def deliveryboydashboard(request):
    # Your view logic goes here
    return render(request, 'deliveryboydashboard.html')
def partsmanagerdashboard(request):
    # Your view logic goes here
    return render(request, 'partsmanagerdashboard.html')

def userdetails(request):
     bookings = ServiceBooking.objects.all()

     return render(request, 'userdetails.html', {'bookings': bookings})
  
    # Your view logic goes here

def service_branch(request):
    # Fetch users with the "Worker" role
    service_center = CustomUser.objects.filter(role='service_center')
    service_center_count = service_center.count()
    print("Service Center Count:", service_center_count)

    return render(request, 'service_branch.html', {'service_center': service_center, 'service_center_count': service_center_count})

def userprofile(request):
    # Fetch users with the "Worker" role
    users = CustomUser.objects.filter(role='user')
    return render(request, 'userprofile.html', {'users': users})

def parts_managers(request):
    # Fetch users with the "Worker" role
    parts_managers = CustomUser.objects.filter(role='parts_manager')

    return render(request, 'parts_managers.html', {'parts_managers': parts_managers})

    
def parts_add(request):
    if request.method == 'POST':
        form = PartForm(request.POST, request.FILES)
        if form.is_valid():
            
            partsname = form.cleaned_data['partsname']
            parts_image = form.cleaned_data['parts_image']
            categories = form.cleaned_data['categories']
            discount = form.cleaned_data['discount']
            additional_details = form.cleaned_data['additional_details']
            if not Parts.objects.filter(
                partsname=partsname,
                parts_image=parts_image,
                categories=categories
                
            ).exists():
                # If not, save the form
                form.save()
                messages.success(request, 'Part added successfully!')
                return redirect('parts_add')
            form.add_error('partsname', 'A part with this name already exists.')
            form.add_error('parts_image', 'A part with this image already exists.')

    else:
        form = PartForm()
    return render(request, 'parts_add.html', {'form': form})
# def parts_list(request):
#     parts_orders = Parts.objects.all()  # Query all the added parts
#     return render(request, 'parts_list.html', {'parts_orders': parts_orders})

# def parts_list(request):
#     parts_orders = Parts.objects.all()  # Query all the added parts
#     categories = Parts.objects.values_list('categories', flat=True).distinct()  # Fetch distinct categories
#     return render(request, 'parts_list.html', {'parts_orders': parts_orders, 'categories': categories})
def parts_list(request):
    parts_orders = Parts.objects.all()  # Fetch all parts
    categories = Parts.objects.values_list('categories', flat=True).distinct()  # Fetch distinct categories
    return render(request, 'parts_list.html', {'parts_orders': parts_orders, 'categories': categories})

def delete_part(request, part_id):
    if request.method == 'POST':
        parts = Parts.objects.get(pk=part_id)
        parts.delete()
    return redirect('parts_list')
    
def update_part(request, part_id):
    parts = get_object_or_404(Parts, id=part_id)

    if request.method == 'POST':
        form = PartForm(request.POST, request.FILES, instance=parts)
        if form.is_valid():
            form.save()
            return redirect('parts_list')  # Redirect to the parts list page after updating
    else:
        form = PartForm(instance=parts)

    return render(request, 'update_part.html', {'form': form, 'parts': parts})

def delete_branch(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=user_id)
        user.delete()
    return redirect('service_branch')
def download_parts_list(request):
    # Query all the added parts
    parts_orders = Parts.objects.all()

    # Create a response with PDF content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="parts_list.pdf"'

    # Create a PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Create a list to hold table data
    table_data = [['Part ID', 'Part Name', 'Description', 'Image']]


    for part in parts_orders:
        row = [part.id, part.partsname, part.description, '']
        if part.parts_image:  # Adjust the field name for the image
            image_path = part.parts_image.path
            image = Image(image_path, width=50, height=50)
            row[-1] = image

        table_data.append(row)

    # Create the table and set styles
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Build the PDF document
    doc.build([table])

    return response
# @login_required
# def add_to_cart(request, product_id):
#     # Retrieve the product and user
#     product = Parts.objects.get(id=product_id)
#     user = request.user

#     # Check if the product is already in the user's cart
#     cart_item, created = CartItem.objects.get_or_create(user=user, product=product)

#     if not created:
#         cart_item.quantity += 1
#         cart_item.save()

#     return JsonResponse({'success': True})

# @login_required
# def view_cart(request):
#     # user = request.user
#     # cart_items = CartItem.objects.filter(user=user)
#     # return render(request, 'view_cart.html', {'cart_items': cart_items})
#     user = request.user
#     cart_items = CartItem.objects.filter(user=user)

#     # Calculate total price
#     total_price = sum(item.product.price * item.quantity for item in cart_items)

#     return render(request, 'view_cart.html', {'cart_items': cart_items, 'total_price': total_price})
@login_required
def view_wishlist(request):
    user = request.user
    wishlist_items = WishlistItem.objects.filter(user=user)
    return render(request, 'view_wishlist.html', {'wishlist_items': wishlist_items})
def add_to_wishlist(request, product_id):
    try:
        product = Parts.objects.get(pk=product_id)
    except Parts.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'})

    # Check if the product is already in the user's wishlist
    if WishlistItem.objects.filter(user=request.user, product=product).exists():
        return JsonResponse({'success': False, 'message': 'Product is already in your wishlist'})

    # If the product is not in the wishlist, add it
    WishlistItem.objects.create(user=request.user, product=product)

    return JsonResponse({'success': True, 'message': 'Product added to your wishlist'})
  # Redirect to your cart view
def all_products(request):
    products = products.objects.all()  # Retrieve all products
    return render(request, 'all_products.html', {'products': products})

# def remove_from_cart(request, product_id):
#     # Assuming your CartItem model has a unique identifier field, e.g., id
#     try:
#         cart_items = CartItem.objects.get(id=product_id)
#         cart_items.delete()
#         success = True
#     except CartItem.DoesNotExist:
#         success = False

#     return JsonResponse({'success': success})


def confirm_booking(request, booking_id):
    # Get the booking using the provided booking_id (you might need to implement this part)
    booking = ServiceBooking.objects.get(pk=booking_id)

    # Update the status of the booking to 'Confirmed'
    booking.status = 'Confirmed'
    booking.save()
    booking_details = (
        f"username: {booking.user}\n"
        f"Driver Number: {booking.driver_number}\n"
        f"Vehicle Number: {booking.vehicle_number}\n"
        f"Service Branch: {booking.service_branch}\n"
        f"Service Date: {booking.service_date}\n"
    )
    # Send an email to the user confirming the booking
    subject = 'Booking Confirmation'
    message = f'Your booking has been confirmed.\n\nBooking Details:\n{booking_details}'
    from_email = 'ava.mi2001@gmail.com'  # Replace with your email address
    recipient_list = [booking.email]  # Assuming email is a field in your ServiceBooking model
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    # Redirect to a page or perform any additional actions
    return HttpResponseRedirect(reverse('userdetails') + f'?user_id={booking.user.id}&booking_id={booking.id}')

def reject_booking(request, booking_id):
    # Get the booking using the provided booking_id (you might need to implement this part)
    booking = ServiceBooking.objects.get(pk=booking_id)

    # Update the status of the booking to 'Rejected'
    booking.status = 'Rejected'
    booking.save()

    # Send an email to the user rejecting the booking
    subject = 'Booking Rejection'
    message = 'Your booking has been rejected.'
    from_email = 'ava.mi2001@gmail.com'  # Replace with your email address
    recipient_list = [booking.email]  # Assuming email is a field in your ServiceBooking model
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    
    # Redirect to a page or perform any additional actions
    return HttpResponseRedirect(reverse('userdetails') + f'?user_id={booking.user.id}&booking_id={booking.id}')


def add_worker(request):
    if request.method == 'POST':
        form = WorkerForm(request.POST)
        if form.is_valid():
            # Save the new worker to the database
            worker = form.save()
            
            # Get the newly created worker's details
            id = worker.id
            username = worker.username 
            email = worker.email 
            password = worker.password  
            
            # Compose the email content
            subject = 'Your Account Details'
            html_message = render_to_string('user_info.html', {'id': id,'username': username,'email': email, 'password': password,})
            plain_message = strip_tags(html_message)  # Strip HTML tags for plain text email
            from_email = 'ava.mi2001@gmail.com.com'  # Replace with your email
            to_email = worker.email  # Assuming 'email' is a field in your Worker model
            
            # Send the email
            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
            
            return redirect('admindashboard')  # Redirect to the worker list page after adding a worker
    else:
        form = WorkerForm()

    return render(request, 'add_worker.html', {'form': form})
# def buy_now_view(request, product_id):
#     try:
#         product = Parts.objects.get(id=product_id)
#         # Assuming 'partsname' and 'price' are fields in your Parts model
#         product_name = product.partsname
#         product_price = product.price
        
#         return render(request, 'buy_now.html', {'product_name': product_name, 'product_price': product_price})
#     except Parts.DoesNotExist:
#         return HttpResponse("Product does not exist.")
@login_required(login_url='login')
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Process form data manually
        user_profile.first_name = request.POST.get('first_name')
        user_profile.last_name = request.POST.get('last_name')
        user_profile.phone_number = request.POST.get('phone_number')
        user_profile.address = request.POST.get('address')
        user_profile.pincode = request.POST.get('pincode')
        user_profile.city = request.POST.get('city')
        user_profile.state = request.POST.get('state')
        # Handle image upload manually
        if 'image' in request.FILES:
            user_profile.image = request.FILES['image']

        user_profile.save()
        request.session['profile_image_updated'] = True
        # Redirect to a success page or update the current page as needed
        return redirect('index')

    return render(request, 'edit_profile.html', {'user_profile': user_profile, 'created':created})

# @login_required
# def booking(request):
#     user_profile = UserProfile.objects.get(user=request.user)

#     if request.method == 'POST':
#         user = request.user
#         email = request.POST.get('email')
#         driver_number = request.POST.get('driver_number')
#         vehicle_number = request.POST.get('vehicle_number')
#         service_branch = request.POST.get('service_branch')
#         vehicle_model = request.POST.get('vehicle_model')
#         service_type = request.POST.get('service_type')
#         file_upload = request.FILES.get('file_upload')
#         file_path = None

#         # Check if the file_upload field is present in request.FILES
#         # Inside the booking view
#         if 'file_upload' in request.FILES:
#             file_upload = request.FILES['file_upload']
    
#             # Save the file to a specific directory
#             file_path = f'uploads/{user.username}_{file_upload.name}'
#             print("File Path:", file_path)
    
#             with default_storage.open(file_path, 'wb+') as destination:
#                 for chunk in file_upload.chunks():
#                     destination.write(chunk)


#         service_date = request.POST.get('service_date')
#         selected_slot = request.POST.get('selected_slot')

#         # Create a ServiceBooking object and save it to the database
#         booking = ServiceBooking.objects.create(
#             user=user,
#             email=email,
#             driver_number=driver_number,
#             vehicle_number=vehicle_number,
#             service_branch=service_branch,
#             vehicle_model=vehicle_model,
#             service_type=service_type,
#             service_date=service_date,
#             file_upload=file_path,
#             time_slot=selected_slot
#         )
#         booking.file_upload = file_path
#         booking.save()
#         confirmation_message = "Booking completed successfully!"
#         return render(request, 'Timeslot.html', {'message': confirmation_message})

#     else:
#         return render(request, 'booking.html', {'user_profile': user_profile})


@login_required
def booking(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        user = request.user
        email = request.POST.get('email')
        driver_number = request.POST.get('driver_number')
        vehicle_number = request.POST.get('vehicle_number')
        service_branch = request.POST.get('service_branch')
        vehicle_model = request.POST.get('vehicle_model')
        service_type = request.POST.get('service_type')

        file_upload = request.FILES.get('file_upload')
        file_path = None

        # Check if the service type is "free" and a file is uploaded
        if service_type == 'free' and file_upload:
            file_path = f'uploads/{user.username}_{file_upload.name}'
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in file_upload.chunks():
                    destination.write(chunk)

        service_date = request.POST.get('service_date')
        selected_slot = request.POST.get('selected_slot')

        # Create a ServiceBooking object and save it to the database
        booking = ServiceBooking.objects.create(
            user=user,
            email=email,
            driver_number=driver_number,
            vehicle_number=vehicle_number,
            service_branch=service_branch,
            vehicle_model=vehicle_model,
            service_type=service_type,
            service_date=service_date,
            time_slot=selected_slot
        )

        # Check if file_path is assigned a value before using it
        if file_path:
            booking.file_upload = file_path
            booking.save()

        confirmation_message = "Booking completed successfully!"
        return render(request, 'Timeslot.html', {'message': confirmation_message})
   
    else:
        return render(request, 'booking.html', {'user_profile': user_profile})



@login_required
def select_time_slot(request):
    if request.method == 'POST':
        slot_number = request.POST.get('slot_number')  # Get the selected time slot
        if slot_number:
            latest_booking = ServiceBooking.objects.filter(user=request.user).latest('id')
            latest_booking.time_slot = slot_number
            latest_booking.save()
            confirmation_message = "Time slot selected successfully!"
            return render(request, 'index.html', {'message': confirmation_message})
        else:
            error_message = "Please select a time slot."
            return render(request, 'Timeslot.html', {'error_message': error_message})
    else:
        return render(request, 'Timeslot.html')



#filter product code
def filter_by_price(request):
    if request.method == 'POST':
        min_price = request.POST.get('min-price')
        max_price = request.POST.get('max-price')
        
        # Filter products based on price range
        filtered_products = Parts.objects.filter(price__range=(min_price, max_price))
        
        # Pass the filtered products to the template
        return render(request, 'partsorder.html', {'filtered_products': filtered_products})

    return render(request, 'partsorder.html')
#change password
@login_required
def change_password(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=request.user.pk)  # Fetch the user
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        
        # Check if 'confirm_new_password' is in request.POST
        if 'confirm_new_password' in request.POST:
            confirm_new_password = request.POST['confirm_new_password']
            # Authenticate the user to verify the current password
            if authenticate(username=user.username, password=current_password):
                if new_password == confirm_new_password:
                    user.set_password(new_password)  # Change the password
                    user.save()
                    update_session_auth_hash(request, user) # Re-authenticate the user
                    return redirect('index')
                    # Redirect to a success URL or render a success message
                else:
                    # Passwords don't match, show an error message
                    error_message = 'New passwords do not match.'
                    return render(request, 'change_password.html', {'error_message': error_message})
            else:
                # Incorrect current password, show an error message
                error_message = 'Current password is incorrect.'
                return render(request, 'change_password.html', {'error_message': error_message})
        else:
            # Handle the case where 'confirm_new_password' is not in request.POST
            error_message = 'Confirm new password field is missing.'
            return render(request, 'change_password.html', {'error_message': error_message})
    else:
        return render(request, 'change_password.html',{'user_profile': user_profile})

@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = Parts.objects.get(pk=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem1.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    categories = product.categories
    return redirect('parts_order_category',category=categories)
    
# @login_required(login_url='login')
# def add_to_cart(request, part_id):
#     part = get_object_or_404(Parts, id=part_id)

#     if part.quantity > 0:
#         # Decrease the available quantity by 1 and save the part
#         part.quantity -= 1
#         part.save()

#         # Check if the user has a cart, create one if not
#         cart, created = Cart.objects.get_or_create(user=request.user)

#         # Check if the item is already in the cart, update quantity if so
#         cart_item, item_created = CartItem1.objects.get_or_create(cart=cart, product=part)

#         if not item_created:
#             cart_item.quantity += 1
#             cart_item.save()

#         messages.success(request, 'Part added to cart successfully!')
#     else:
#         messages.warning(request, 'This part is out of stock.')

#     # Redirect to the appropriate category page after adding to cart
#     return redirect('parts_order_category', category=part.categories)
@login_required(login_url='login')
def remove_from_cart(request, product_id):
    product = Parts.objects.get(pk=product_id)
    cart = Cart.objects.get(user=request.user)
    try:
        cart_item = CartItem1.objects.get(cart=cart, product=product)
        if cart_item.quantity >= 1:
            cart_item.delete()
    except CartItem1.DoesNotExist:
        pass
   
    return redirect('view_cart')

@login_required(login_url='login')
def view_cart(request):
    user_profile = UserProfile.objects.get(user=request.user)
    cart = request.user.cart
    cart_items = CartItem1.objects.filter(cart=cart)
    return render(request, 'view_cart.html', {'cart_items': cart_items,'user_profile': user_profile,})

@login_required(login_url='login')
def increase_cart_item(request, product_id):
    product = Parts.objects.get(pk=product_id)
    cart = request.user.cart
    cart_item, created = CartItem1.objects.get_or_create(cart=cart, product=product)

    cart_item.quantity += 1
    cart_item.save()

    return redirect('view_cart')

@login_required(login_url='login')
def decrease_cart_item(request, product_id):
    product = Parts.objects.get(pk=product_id)
    cart = Cart.objects.get(user=request.user)
    
    try:
        cart_item = cart.cartitem1_set.get(product=product)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()

    except CartItem1.DoesNotExist:
        pass

    return redirect('view_cart')
    
@login_required(login_url='login')
def fetch_cart_count(request):
    cart_count = 0
    if request.user.is_authenticated:
        cart = request.user.cart
        cart_count = CartItem1.objects.filter(cart=cart).count()
    return JsonResponse({'cart_count': cart_count})
def get_cart_count(request):
    if request.user.is_authenticated:
        cart_items = CartItem1.objects.filter(cart=request.user.cart)
        cart_count = cart_items.count()
    else:
        cart_count = 0
    return cart_count

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        user = request.user
        cart = user.cart

        cart_items = CartItem1.objects.filter(cart=cart)
        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        try:
            order = Order.objects.create(user=user, total_amount=total_amount)
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    item_total=cart_item.product.price * cart_item.quantity
                )

            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            payment_data = {
                'amount': int(total_amount * 100),
                'currency': 'INR',
                'receipt': f'order_{order.id}',
                'payment_capture': '1'
            }
            orderData = client.order.create(data=payment_data)
            order.payment_id = orderData['id']
            order.save()

            return JsonResponse({'order_id': orderData['id']})
        
        except Exception as e:
            print(str(e))
            return JsonResponse({'error': 'An error occurred. Please try again.'}, status=500)
def checkout(request):
    
    cart_items = CartItem1.objects.filter(cart=request.user.cart)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    cart_count = get_cart_count(request)
    email = request.user.email
    username = request.user.username

    context = {
        'cart_count': cart_count,
        'cart_items': cart_items,
        'total_amount': total_amount,
        'email':email,
        'username': username
    }
    return render(request, 'checkout.html',context)
@csrf_exempt
def handle_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        razorpay_order_id = data.get('order_id')
        payment_id = data.get('payment_id')

        try:
            order = Order.objects.get(payment_id=razorpay_order_id)

            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            payment = client.payment.fetch(payment_id)

            if payment['status'] == 'captured':
                order.payment_status = True
                order.save()
                # user = request.user
                # user.cart.cartitem_set.all().delete()
                return JsonResponse({'message': 'Payment successful'})
            else:
                return JsonResponse({'message': 'Payment failed'})

        except Order.DoesNotExist:
            return JsonResponse({'message': 'Invalid Order ID'})
        except Exception as e:

            print(str(e))
            return JsonResponse({'message': 'Server error, please try again later.'})

def order_details_api(request, order_id):
    # Your logic to retrieve order details based on order_id
    # ...

    # Return order details as a JSON response
    order_details = {
        # ...
    }
    return JsonResponse(order_details)
def bill_invoice(request):
    # Fetch the latest order for the logged-in user (or implement your logic)
    order = Order.objects.filter(user=request.user).latest('created_at')
    return render(request, 'billinvoice.html', {'order': order})
def view_more(request, part_id):
    part = get_object_or_404(Parts, id=part_id)
    return render(request, 'view_more.html', {'part': part})


def Vehicle_Add(request):
    if request.method == 'POST':
        vehiclename = request.POST.get('vehiclename')
        description = request.POST.get('description')
        price = request.POST.get('price')
        discount = request.POST.get('discount')
        vehiclemodel = request.POST.get('vehiclemodel')
        vehicleusage = request.POST.get('vehicleusage')
        vehicleapplication = request.POST.get('vehicleapplication')
        fueltype = request.POST.get('fueltype')
        transmissiontype = request.POST.get('transmissiontype')
        enginesize = request.POST.get('enginesize')
        mileage = request.POST.get('mileage')
        warranty = request.POST.get('warranty')
        seatingcapacity = request.POST.get('seatingcapacity')
        fueltankcapacity = request.POST.get('fueltankcapacity')
        vehiclecolors = request.POST.getlist('vehiclecolors')
        vehiclestock = request.POST.get('vehiclestock')

        # Create a new vehicle instance
        vehicle = Vehicle.objects.create(
            name=vehiclename,
            description=description,
            price=price,
            discount=discount,
            vehicle_model=vehiclemodel,
            vehicle_usage=vehicleusage,
            vehicle_application=vehicleapplication,
            fuel_type=fueltype,
            transmission_type=transmissiontype,
            engine_size=enginesize,
            mileage=mileage,
            warranty=warranty,
            seating_capacity=seatingcapacity,
            fuel_tank_capacity=fueltankcapacity,
            stock=vehiclestock
        )

        # Associate multiple images with the created vehicle
        images = request.FILES.getlist('image')
        for image in images:
            VehicleImage.objects.create(vehicle=vehicle, image=image)

        messages.success(request, 'Vehicle added successfully!')
        return redirect('Vehicle_Add')  # Redirect to a success page

    return render(request, 'Vehicle_Add.html')

def vehicleorder(request, model):
    # Filter vehicles based on the selected model
    vehicles = Vehicle.objects.filter(vehicle_model=model)

    return render(request, 'vehicleorder.html', {'model': model, 'vehicles': vehicles})
def vehicle_list(request):
    vehicles = Vehicle.objects.all()  # Fetch all vehicles, adjust the queryset as needed
    return render(request, 'Vehicle_list.html', {'vehicles': vehicles})

def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == 'POST':
        # Delete associated images
        vehicle.images.all().delete()

        # Delete the vehicle
        vehicle.delete()

        return JsonResponse({'message': 'Vehicle deleted successfully!'})

    return JsonResponse({'error': 'Invalid request method'})
def vehicle_details(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    return render(request, 'vehicle_details.html', {'vehicle': vehicle})