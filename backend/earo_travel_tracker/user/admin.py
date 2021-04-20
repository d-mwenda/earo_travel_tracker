# """
# Register models with admin
# """
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import User as DjangoUser

# from user.models import User as CustomUser


# # which acts a bit like a singleton
# class UserInline(admin.StackedInline):
#     """
#     Define an inline admin descriptor for User model
#     """
#     model = CustomUser
#     can_delete = False
#     verbose_name_plural = 'users'


# class UserAdmin(BaseUserAdmin):
#     """
#     Define a new User admin
#     """
#     inlines = (UserInline,)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.site.register(User, UserAdmin)


# # Re-register UserAdmin
# admin.site.unregister(DjangoUser)
# admin.site.register(CustomUser, UserAdmin)
