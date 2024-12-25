from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Product, Waiter

# Register the custom user model with the customized admin
User = get_user_model()
admin.site.register(User)

# Register the Product model
admin.site.register(Product)

# Register the Waiter model
admin.site.register(Waiter)