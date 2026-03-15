from django.contrib import admin
from .models import Fee, StudentFee


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'amount')
    list_filter = ('school',)
    search_fields = ('name',)


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee', 'amount_paid', 'due_date', 'paid')
    list_filter = ('paid', 'due_date')
    search_fields = ('student__first_name', 'student__last_name')
