from django.core.management.base import BaseCommand
from django.utils.text import slugify
from listings.models import Category, Condition


class Command(BaseCommand):
    help = 'Populate categories and conditions for the trading platform'

    def handle(self, *args, **options):
        self.stdout.write('Populating categories and conditions...')
        
        # Main categories with icons
        categories_data = [
            {
                'name': 'Electronics',
                'icon': 'laptop',
                'subcategories': [
                    'Mobile Phones', 'Laptops & Computers', 'Tablets', 'Cameras', 'Audio & Headphones',
                    'Gaming', 'Home Appliances', 'TV & Entertainment', 'Smart Watches', 'Accessories'
                ]
            },
            {
                'name': 'Vehicles',
                'icon': 'car',
                'subcategories': [
                    'Cars', 'Motorcycles', 'Bicycles', 'Commercial Vehicles', 'Auto Parts',
                    'Boats', 'Other Vehicles'
                ]
            },
            {
                'name': 'Real Estate',
                'icon': 'home',
                'subcategories': [
                    'Houses for Sale', 'Houses for Rent', 'Apartments', 'Commercial Property',
                    'Land & Plots', 'PG & Hostels', 'Flatmates', 'Office Space'
                ]
            },
            {
                'name': 'Fashion & Beauty',
                'icon': 'tshirt',
                'subcategories': [
                    'Men\'s Clothing', 'Women\'s Clothing', 'Kids\' Clothing', 'Shoes', 'Bags',
                    'Watches', 'Jewelry', 'Beauty Products', 'Ethnic Wear'
                ]
            },
            {
                'name': 'Home & Garden',
                'icon': 'couch',
                'subcategories': [
                    'Furniture', 'Home Decor', 'Kitchen & Dining', 'Garden & Outdoor',
                    'Tools & Hardware', 'Lighting', 'Storage & Organization'
                ]
            },
            {
                'name': 'Sports & Fitness',
                'icon': 'dumbbell',
                'subcategories': [
                    'Gym Equipment', 'Outdoor Sports', 'Cricket', 'Football', 'Badminton',
                    'Cycling', 'Swimming', 'Yoga & Fitness', 'Sports Shoes'
                ]
            },
            {
                'name': 'Books & Education',
                'icon': 'book',
                'subcategories': [
                    'Academic Books', 'Novels & Fiction', 'Children\'s Books', 'Educational Toys',
                    'Musical Instruments', 'Art & Craft', 'Competitive Exam Books'
                ]
            },
            {
                'name': 'Jobs & Services',
                'icon': 'briefcase',
                'subcategories': [
                    'Full Time Jobs', 'Part Time Jobs', 'Freelance', 'Domestic Help',
                    'Repair Services', 'Tutoring', 'Event Services', 'Business Services'
                ]
            },
            {
                'name': 'Pets & Animals',
                'icon': 'paw',
                'subcategories': [
                    'Dogs', 'Cats', 'Birds', 'Fish & Aquarium', 'Pet Accessories',
                    'Pet Food', 'Pet Services', 'Other Pets'
                ]
            },
            {
                'name': 'Agriculture',
                'icon': 'seedling',
                'subcategories': [
                    'Farm Equipment', 'Seeds & Plants', 'Fertilizers', 'Livestock',
                    'Farm Products', 'Agricultural Land', 'Organic Products'
                ]
            },
            {
                'name': 'Baby & Kids',
                'icon': 'baby',
                'subcategories': [
                    'Baby Clothing', 'Toys', 'Baby Gear', 'Kids Furniture', 'Baby Food',
                    'Strollers & Car Seats', 'Educational Toys', 'Baby Care'
                ]
            },
            {
                'name': 'Art & Collectibles',
                'icon': 'palette',
                'subcategories': [
                    'Paintings', 'Sculptures', 'Antiques', 'Coins & Stamps', 'Handicrafts',
                    'Vintage Items', 'Religious Items', 'Decorative Items'
                ]
            }
        ]
        
        # Create categories
        for cat_data in categories_data:
            try:
                parent_category = Category.objects.get(name=cat_data['name'])
                self.stdout.write(f'Category already exists: {parent_category.name}')
            except Category.DoesNotExist:
                parent_category = Category.objects.create(
                    name=cat_data['name'],
                    slug=slugify(cat_data['name']),
                    icon=cat_data['icon'],
                    is_active=True
                )
                self.stdout.write(f'Created category: {parent_category.name}')
            
            # Create subcategories
            for i, subcat_name in enumerate(cat_data['subcategories']):
                try:
                    subcategory = Category.objects.get(name=subcat_name, parent=parent_category)
                    self.stdout.write(f'Subcategory already exists: {subcategory.name}')
                except Category.DoesNotExist:
                    base_slug = slugify(subcat_name)
                    slug = base_slug
                    counter = 1
                    
                    # Handle duplicate slugs
                    while Category.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    subcategory = Category.objects.create(
                        name=subcat_name,
                        parent=parent_category,
                        slug=slug,
                        sort_order=i,
                        is_active=True
                    )
                    self.stdout.write(f'Created subcategory: {subcategory.name}')
        
        # Create conditions
        conditions_data = [
            {'name': 'Brand New', 'description': 'Never used, in original packaging'},
            {'name': 'Like New', 'description': 'Barely used, excellent condition'},
            {'name': 'Good', 'description': 'Used but in good working condition'},
            {'name': 'Fair', 'description': 'Shows wear but still functional'},
            {'name': 'Poor', 'description': 'Heavily used, may need repairs'},
        ]
        
        for i, condition_data in enumerate(conditions_data):
            condition, created = Condition.objects.get_or_create(
                name=condition_data['name'],
                defaults={
                    'description': condition_data['description'],
                    'sort_order': i
                }
            )
            if created:
                self.stdout.write(f'Created condition: {condition.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated categories and conditions!'))
        self.stdout.write(f'Total categories: {Category.objects.count()}')
        self.stdout.write(f'Total conditions: {Condition.objects.count()}')