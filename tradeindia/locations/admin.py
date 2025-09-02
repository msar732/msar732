from django.contrib import admin
from .models import State, District, City


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'code', 'created_at']
    list_filter = ['state', 'created_at']
    search_fields = ['name', 'code', 'state__name']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['state']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'state', 'pincode', 'created_at']
    list_filter = ['state', 'district', 'created_at']
    search_fields = ['name', 'pincode', 'district__name', 'state__name']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['district', 'state']