from django.http import HttpResponse , HttpRequest
from django.shortcuts import render , redirect
from django.contrib.auth.models import User , auth
from django.contrib import messages
from .models import UniqueID

def members(request):
  return render(request , "index1.html" )

def home(request):
  return render(request , "welcome_page.html")

def id(request):
  return render(request ,"uniqueid_create.html")

def log_signup(request):
  return render (request , "login_signup.html")

from django.contrib import messages, auth

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            request.session['username'] = username
            return redirect('uniqueid2')  # Replace 'uniqueid2' with your actual URL name or path
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('login')  # Replace 'login' with your actual login page URL name or path
    else:
        return render(request, 'login.html')
    

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already in use.')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, 'Registration successful. Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

         
def number(request):
  total = request.POST['name']
  totalw = len(total.split())
  context ={
    "total":totalw
  }
  return render(request , "number.html" ,context)

import json
import requests
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def uniqueid1(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            # Get the client's public IP address
            response = requests.get('https://api64.ipify.org?format=json')
            ip = response.json().get('ip')
            
            # Check if the IP already has a unique ID
            unique_id_obj = UniqueID.objects.filter(ip=ip).first()
            if unique_id_obj:
                # If IP already has a unique ID, return it
                return render(request, "uniqueid_create.html", {"uniqueid": unique_id_obj.unique_id})
                
            else:
                # Generate a new unique ID
                new_unique_id = generate_unique_id()
                
                # Save new unique ID to the database
                unique_id_obj = UniqueID.objects.create(
                    unique_id=new_unique_id,
                    latitude=latitude,
                    longitude=longitude,
                    ip=ip
                )
                
                # Return the newly generated unique ID
                response_data = {
                    'status': 'success',
                    'latitude': latitude,
                    'longitude': longitude,
                    'ip': ip,
                    'unique_id': new_unique_id
                }
                return render(request, "uniqueid_create.html", {"uniqueid": new_unique_id})

        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    
    elif request.method == 'GET':
        # Get the client's public IP address
        response = requests.get('https://api64.ipify.org?format=json')
        ip = response.json().get('ip')
        
        # Check if the IP already has a unique ID
        unique_id_obj = UniqueID.objects.filter(ip=ip).first()
        if unique_id_obj:
            # If IP already has a unique ID, return it
           return render(request, "uniqueid_create.html", {"uniqueid": unique_id_obj.unique_id})
          
        else:
            # Generate a new unique ID
            new_unique_id = generate_unique_id()
            
            # Save new unique ID to the database
            unique_id_obj = UniqueID.objects.create(
                unique_id=new_unique_id,
                latitude=None,  # or provide a default value
                longitude=None,  # or provide a default value
                ip=ip
            )
            
            # Return the newly generated unique ID
            response_data = {
                'status': 'success',
                'latitude': None,  # or provide a default value
                'longitude': None,  # or provide a default value
                'ip': ip,
                'unique_id': new_unique_id
            }
            return render(request, "uniqueid_create.html", {"uniqueid": new_unique_id})
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


    
def generate_unique_id():
    # Generate a random unique ID
    return str(random.randint(100000, 999999))

def uniqueid2(request):
    if request.method == 'POST':
        unique_id = request.POST.get('uniqueid')

        if UniqueID.objects.filter(unique_id=unique_id).exists():
            request.session['unique_id'] = unique_id
            return redirect('navigatorhome')  # Redirect to 'navigatorhome' if UniqueID exists
        else:
            messages.error(request, 'Invalid ID')  # Display error message if UniqueID does not exist

    return render(request, 'unique_id_enter.html')
def navigatorhome(request):
   username = request.session.get('username')
   unique_id = request.session.get('unique_id')
   context = {
       "username":username,
        "unique_id":unique_id,
   }
   return render(request , "navigator.html" , context)


def location(request):
    unique_id = request.session.get('unique_id')

    if unique_id:
        try:
            unique_id_obj = UniqueID.objects.get(unique_id=unique_id)
            unique_id_data = {
                'unique_id': unique_id_obj.unique_id,
                'created_at': unique_id_obj.created_at,
                'latitude': unique_id_obj.latitude,
                'longitude': unique_id_obj.longitude,
            }
        except UniqueID.DoesNotExist:
            unique_id_data = {
                'unique_id': None,
                'created_at': None,
                'latitude': None,
                'longitude': None,
            }
    else:
        unique_id_data = {
            'unique_id': None,
            'created_at': None,
            'latitude': None,
            'longitude': None,
        }

    return render(request, "location.html", {'unique_id_data': unique_id_data})
