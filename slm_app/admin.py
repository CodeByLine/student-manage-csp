from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from slm_app.models import CustomUser


class UserModel(UserAdmin):
    pass
# Must create blank UserModel class and registering here in admin.py. 
# Otherwise, passwords wont be encrypted.

admin.site.register(CustomUser,UserModel)