from django.contrib import admin
from .models import Listing, ListingImage, Category, State, District


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'state', 'district', 'price', 'is_featured', 'ai_genuine_score', 'created_at')
    list_filter = ('category', 'state', 'district', 'is_featured', 'is_active')
    search_fields = ('title', 'description')
    inlines = [ListingImageInline]


admin.site.register(ListingImage)
admin.site.register(Category)
admin.site.register(State)
admin.site.register(District)

# Register your models here.
