from django.contrib import admin
from .models import Category, Listing, ListingImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name", "slug")
	search_fields = ("name",)
	prepopulated_fields = {"slug": ("name",)}


class ListingImageInline(admin.TabularInline):
	model = ListingImage
	extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
	list_display = ("title", "owner", "category", "state", "district", "is_verified_ai", "ai_genuineness_score", "created_at")
	list_filter = ("category", "state", "district", "is_verified_ai", "is_active")
	search_fields = ("title", "description", "city", "district", "state")
	inlines = [ListingImageInline]
	readonly_fields = ("slug",)