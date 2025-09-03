from django.contrib import admin
from .models import AIVerificationResult

@admin.register(AIVerificationResult)
class AIVerificationResultAdmin(admin.ModelAdmin):
    list_display = ['listing', 'genuineness_score', 'is_genuine', 'processed_at']
    list_filter = ['is_genuine', 'processed_at']
    search_fields = ['listing__title']
    readonly_fields = ['processed_at']