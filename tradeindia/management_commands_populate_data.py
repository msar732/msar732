# Management Command to Populate Initial Data
from django.core.management.base import BaseCommand
from listings.models import State, District, Category
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populate initial data for states, districts, and categories'

    def handle(self, *args, **options):
        self.stdout.write('Populating database with initial data...')
        
        # India States and Districts data
        states_districts = {
            'Andhra Pradesh': ['Anantapur', 'Chittoor', 'Guntur', 'Krishna', 'Kurnool', 'Nellore', 'Visakhapatnam'],
            'Assam': ['Guwahati', 'Dibrugarh', 'Silchar', 'Jorhat', 'Nagaon', 'Tinsukia'],
            'Bihar': ['Patna', 'Gaya', 'Bhagalpur', 'Muzaffarpur', 'Purnia', 'Darbhanga'],
            'Chhattisgarh': ['Raipur', 'Bilaspur', 'Korba', 'Durg', 'Rajnandgaon'],
            'Delhi': ['Central Delhi', 'East Delhi', 'New Delhi', 'North Delhi', 'South Delhi', 'West Delhi'],
            'Goa': ['North Goa', 'South Goa'],
            'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar'],
            'Haryana': ['Gurgaon', 'Faridabad', 'Hisar', 'Panipat', 'Karnal', 'Ambala'],
            'Himachal Pradesh': ['Shimla', 'Kangra', 'Mandi', 'Kullu', 'Solan', 'Hamirpur'],
            'Jharkhand': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar'],
            'Karnataka': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore', 'Belgaum', 'Gulbarga'],
            'Kerala': ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Thrissur', 'Kollam', 'Palakkad'],
            'Madhya Pradesh': ['Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Ujjain', 'Sagar'],
            'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Aurangabad', 'Solapur', 'Nashik'],
            'Manipur': ['Imphal East', 'Imphal West', 'Bishnupur', 'Thoubal'],
            'Meghalaya': ['East Khasi Hills', 'West Khasi Hills', 'South West Khasi Hills'],
            'Mizoram': ['Aizawl', 'Lunglei', 'Champhai'],
            'Nagaland': ['Kohima', 'Dimapur', 'Mokokchung'],
            'Odisha': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Berhampur', 'Sambalpur'],
            'Punjab': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda'],
            'Rajasthan': ['Jaipur', 'Jodhpur', 'Kota', 'Bikaner', 'Ajmer', 'Udaipur'],
            'Sikkim': ['Gangtok', 'Namchi', 'Gyalshing', 'Mangan'],
            'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli'],
            'Telangana': ['Hyderabad', 'Warangal', 'Nizamabad', 'Khammam', 'Karimnagar'],
            'Tripura': ['Agartala', 'Dharmanagar', 'Udaipur', 'Kailasahar'],
            'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Ghaziabad', 'Agra', 'Meerut', 'Varanasi'],
            'Uttarakhand': ['Dehradun', 'Haridwar', 'Roorkee', 'Haldwani', 'Kashipur'],
            'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri']
        }
        
        # Create states and districts
        for state_name, districts in states_districts.items():
            state_code = state_name.replace(' ', '').upper()[:3]
            state, created = State.objects.get_or_create(
                name=state_name,
                defaults={'code': state_code}
            )
            if created:
                self.stdout.write(f'Created state: {state_name}')
            
            for district_name in districts:
                district, created = District.objects.get_or_create(
                    name=district_name,
                    state=state
                )
                if created:
                    self.stdout.write(f'Created district: {district_name}, {state_name}')

        # Categories data
        categories_data = [
            {'name': 'Electronics & Gadgets', 'icon': 'fas fa-mobile-alt', 'description': 'Mobile phones, laptops, cameras, and electronic devices'},
            {'name': 'Vehicles', 'icon': 'fas fa-car', 'description': 'Cars, bikes, scooters, and automotive parts'},
            {'name': 'Property', 'icon': 'fas fa-home', 'description': 'Houses, apartments, plots, and commercial spaces'},
            {'name': 'Fashion & Beauty', 'icon': 'fas fa-tshirt', 'description': 'Clothing, accessories, cosmetics, and jewelry'},
            {'name': 'Home & Furniture', 'icon': 'fas fa-couch', 'description': 'Furniture, home decor, and household items'},
            {'name': 'Jobs & Services', 'icon': 'fas fa-briefcase', 'description': 'Job postings and professional services'},
            {'name': 'Books & Sports', 'icon': 'fas fa-book', 'description': 'Books, educational materials, and sports equipment'},
            {'name': 'Pets & Animals', 'icon': 'fas fa-paw', 'description': 'Pets, pet accessories, and animal care'},
            {'name': 'Business & Industrial', 'icon': 'fas fa-industry', 'description': 'Business equipment and industrial machinery'},
            {'name': 'Agriculture', 'icon': 'fas fa-seedling', 'description': 'Agricultural products, tools, and livestock'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'icon': cat_data['icon'],
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created category: {cat_data["name"]}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))