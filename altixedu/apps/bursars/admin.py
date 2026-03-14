from django.contrib import admin
from .models import Bursar


@admin.register(Bursar)
class BursarAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'school', 'created_at')
    list_filter = ('school', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {'fields': ('user', 'school')}),
        ('Fee Management', {'fields': ('managed_fees',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
