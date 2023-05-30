from django.contrib import admin

# Register your models here.
from .models import News
from .models import CustomUser
admin.site.register(CustomUser)
admin.site.register(News)