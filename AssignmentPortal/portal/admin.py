

# Register your models here.
from django.contrib import admin
from .models import Assignment, Submission

# Custom admin classes
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'deadline', 'created_at')  # Fields to show in list view
    search_fields = ('title',)  # Enable search by title

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'grade')  # Fields to show
    list_filter = ('assignment',)  # Filter by assignment

# Register models with custom admin
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Submission, SubmissionAdmin)