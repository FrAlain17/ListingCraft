from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'company_name', 'phone', 'avatar')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('email', 'first_name', 'last_name', 'get_role', 'get_company', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'profile__role')
    search_fields = ('email', 'first_name', 'last_name', 'profile__company_name')

    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else '-'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'profile__role'

    def get_company(self, obj):
        return obj.profile.company_name if hasattr(obj, 'profile') else '-'
    get_company.short_description = 'Company'
    get_company.admin_order_field = 'profile__company_name'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'role', 'company_name', 'phone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__email', 'company_name', 'phone')
    readonly_fields = ('created_at', 'updated_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
