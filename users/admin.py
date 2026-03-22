from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User

    # what to show in list view
    list_display = ("username", "email", "role", "is_staff", "is_active")

    # IMPORTANT: show role in edit page
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("role",)}),
    )

    # IMPORTANT: show role when creating user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("email", "role")}),
    )


admin.site.register(User, CustomUserAdmin)