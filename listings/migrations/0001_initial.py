from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

	initial = True

	dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
	]

	operations = [
		migrations.CreateModel(
			name='Category',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('name', models.CharField(max_length=120, unique=True)),
				('slug', models.SlugField(blank=True, max_length=140, unique=True)),
			],
		),
		migrations.CreateModel(
			name='Listing',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('title', models.CharField(max_length=160)),
				('description', models.TextField()),
				('listing_type', models.CharField(choices=[('sell', 'Sell'), ('rent', 'Rent'), ('service', 'Service')], default='sell', max_length=16)),
				('price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
				('state', models.CharField(db_index=True, max_length=100)),
				('district', models.CharField(db_index=True, max_length=100)),
				('city', models.CharField(blank=True, default='', max_length=120)),
				('address', models.CharField(blank=True, default='', max_length=255)),
				('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
				('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
				('is_active', models.BooleanField(default=True)),
				('is_verified_ai', models.BooleanField(default=False)),
				('ai_genuineness_score', models.FloatField(default=0.0)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				('slug', models.SlugField(blank=True, max_length=220, unique=True)),
				('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='listings', to='listings.category')),
				('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listings', to=settings.AUTH_USER_MODEL)),
			],
			options={
				'ordering': ['-created_at'],
			},
		),
		migrations.CreateModel(
			name='ListingImage',
			fields=[
				('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('image', models.ImageField(upload_to='listings/%Y/%m/')),
				('caption', models.CharField(blank=True, max_length=200)),
				('is_primary', models.BooleanField(default=False)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='listings.listing')),
			],
			options={
				'ordering': ['-is_primary', '-created_at'],
			},
		),
		migrations.AddIndex(
			model_name='listing',
			index=models.Index(fields=['state', 'district'], name='listings_li_state__6cb13a_idx'),
		),
		migrations.AddIndex(
			model_name='listing',
			index=models.Index(fields=['is_active', 'is_verified_ai', 'ai_genuineness_score'], name='listings_li_is_acti_8bdab9_idx'),
		),
	]