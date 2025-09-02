from django import forms
from .models import Listing, ListingImage


class ListingForm(forms.ModelForm):
	images = forms.FileField(widget=forms.ClearableFileInput(attrs={"multiple": True}), required=False)

	class Meta:
		model = Listing
		fields = [
			"title",
			"description",
			"category",
			"listing_type",
			"price",
			"state",
			"district",
			"city",
			"address",
			"latitude",
			"longitude",
		]

	def save(self, owner, commit=True):
		listing: Listing = super().save(commit=False)
		listing.owner = owner
		if commit:
			listing.save()
			images = self.files.getlist("images")
			for idx, image in enumerate(images):
				ListingImage.objects.create(listing=listing, image=image, is_primary=idx == 0)
		return listing