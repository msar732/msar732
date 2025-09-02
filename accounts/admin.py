from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Profile', {'fields': ('phone', 'avatar')}),
    )
    list_display = ('id', 'username', 'email', 'phone', 'is_staff')

# Register your models here.
