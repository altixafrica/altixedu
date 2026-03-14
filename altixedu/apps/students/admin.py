from django.contrib import admin
from .models import Student, StudentParent, Parent


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'admission_number', 'school', 'user', 'status')
    list_filter = ('school', 'status', 'gender')
    search_fields = ('first_name', 'last_name', 'admission_number', 'user__email')
    readonly_fields = ()


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'school', 'phone')
    list_filter = ('school',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'phone')
    readonly_fields = ()
    
    fieldsets = (
        ('Basic Info', {'fields': ('user', 'school')}),
        ('Contact', {'fields': ('phone', 'address')}),
    )


@admin.register(StudentParent)
class StudentParentAdmin(admin.ModelAdmin):
    list_display = ('student', 'parent', 'relationship')
    list_filter = ('relationship',)
    search_fields = ('student__first_name', 'parent__user__first_name', 'parent__user__last_name')
