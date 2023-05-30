from django.urls import path
from . import views

urlpatterns = [
        path("", views.index, name="index"),
        path('login.html',views.login,name="login"),
        path('signup.html',views.signup,name="signup"),
        path('contactus.html',views.contactus,name="contactus"),
        path('index.html',views.index,name="index"),
        path("logout",views.logout_view,name="logout")


]
