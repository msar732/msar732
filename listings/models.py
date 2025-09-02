from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.urls import reverse

User = get_user_model()


class Category(models.Model):
	name = models.CharField(max_length=120, unique=True)
	slug = models.SlugField(max_length=140, unique=True, blank=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	def __str__(self) -> str:
		return self.name


class Listing(models.Model):
	SELL = "sell"
	RENT = "rent"
	SERVICE = "service"
	TYPE_CHOICES = (
		(SELL, "Sell"),
		(RENT, "Rent"),
		(SERVICE, "Service"),
	)
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
	title = models.CharField(max_length=160)
	description = models.TextField()
	category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="listings")
	listing_type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=SELL)
	price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
	state = models.CharField(max_length=100, db_index=True)
	district = models.CharField(max_length=100, db_index=True)
	city = models.CharField(max_length=120, blank=True, default="")
	address = models.CharField(max_length=255, blank=True, default="")
	latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
	longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
	is_active = models.BooleanField(default=True)
	is_verified_ai = models.BooleanField(default=False)
	ai_genuineness_score = models.FloatField(default=0.0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	slug = models.SlugField(max_length=220, unique=True, blank=True)

	class Meta:
		ordering = ["-created_at"]
		indexes = [
			models.Index(fields=["state", "district"]),
			models.Index(fields=["is_active", "is_verified_ai", "ai_genuineness_score"]),
		]

	def save(self, *args, **kwargs):
		if not self.slug:
			base = slugify(self.title)[:60]
			self.slug = f"{base}-{self.pk or ''}" if base else slugify(str(self.pk or ''))
		super().save(*args, **kwargs)
		if f"{self.pk}" not in self.slug:
			self.slug = f"{slugify(self.title)[:60]}-{self.pk}"
			super().save(update_fields=["slug"])

	@property
	def location_display(self) -> str:
		bits = [self.city, self.district, self.state]
		return ", ".join([b for b in bits if b])

	def get_absolute_url(self):
		return reverse("listings:detail", kwargs={"slug": self.slug})


class ListingImage(models.Model):
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="images")
	image = models.ImageField(upload_to="listings/%Y/%m/")
	caption = models.CharField(max_length=200, blank=True)
	is_primary = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-is_primary", "-created_at"]

	def __str__(self) -> str:
		return f"Image for {self.listing_id}"