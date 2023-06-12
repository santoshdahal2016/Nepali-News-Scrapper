from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from app.models.user import User

class Admin(UserAdmin):
    model = User
    list_display = ('email', 'is_active', 'user_id')
    list_filter = ('email', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        # ('Permissions', {'fields': ('is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide'),
            'fields': ('email', 'password1', 'password2', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(User, Admin)


