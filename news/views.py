from django.shortcuts import render

# Create your views here.

from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import CustomUser

#from django.contrib import massages
from .models import News
# Create your views here.
def index(request):
 news = News.objects.all()
 return render(request, "index.html", {'news': news,'user': request.user})
def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            auth_login(request, user)  # Renamed to auth_login to avoid conflict
            return redirect("/")
        else:
            # Handle invalid login credentials
            return render(request, "login.html", {"error": "Invalid email or password."})
    else:
        return render(request, "login.html")

def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']

        try:
            # Check if the email is already registered
            existing_user = CustomUser.objects.get(email=email)
            return render(request, "signup.html", {"error": "Email already registered."})
        except CustomUser.DoesNotExist:
            # Create a new user
            user = CustomUser.objects.create_user(email=email, username=username, password=password)
            
            # Log in the newly registered user
            auth_login(request, user)  # Renamed to auth_login to avoid conflict
            return redirect("/")
    else:
        return render(request, "signup.html")


def logout_view(request):
    auth_logout(request)  # Renamed to auth_logout to avoid conflict
    return redirect("/")
def contactus(request):
    return render(request,"contactus.html") 