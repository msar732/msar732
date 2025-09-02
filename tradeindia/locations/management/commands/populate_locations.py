from django.core.management.base import BaseCommand
from locations.models import State, District, City


class Command(BaseCommand):
    help = 'Populate Indian states, districts and major cities'

    def handle(self, *args, **options):
        self.stdout.write('Populating Indian locations...')
        
        # Indian states and union territories data
        states_data = [
            {'name': 'Andhra Pradesh', 'code': 'AP'},
            {'name': 'Arunachal Pradesh', 'code': 'AR'},
            {'name': 'Assam', 'code': 'AS'},
            {'name': 'Bihar', 'code': 'BR'},
            {'name': 'Chhattisgarh', 'code': 'CG'},
            {'name': 'Goa', 'code': 'GA'},
            {'name': 'Gujarat', 'code': 'GJ'},
            {'name': 'Haryana', 'code': 'HR'},
            {'name': 'Himachal Pradesh', 'code': 'HP'},
            {'name': 'Jharkhand', 'code': 'JH'},
            {'name': 'Karnataka', 'code': 'KA'},
            {'name': 'Kerala', 'code': 'KL'},
            {'name': 'Madhya Pradesh', 'code': 'MP'},
            {'name': 'Maharashtra', 'code': 'MH'},
            {'name': 'Manipur', 'code': 'MN'},
            {'name': 'Meghalaya', 'code': 'ML'},
            {'name': 'Mizoram', 'code': 'MZ'},
            {'name': 'Nagaland', 'code': 'NL'},
            {'name': 'Odisha', 'code': 'OR'},
            {'name': 'Punjab', 'code': 'PB'},
            {'name': 'Rajasthan', 'code': 'RJ'},
            {'name': 'Sikkim', 'code': 'SK'},
            {'name': 'Tamil Nadu', 'code': 'TN'},
            {'name': 'Telangana', 'code': 'TG'},
            {'name': 'Tripura', 'code': 'TR'},
            {'name': 'Uttar Pradesh', 'code': 'UP'},
            {'name': 'Uttarakhand', 'code': 'UK'},
            {'name': 'West Bengal', 'code': 'WB'},
            {'name': 'Andaman and Nicobar Islands', 'code': 'AN'},
            {'name': 'Chandigarh', 'code': 'CH'},
            {'name': 'Dadra and Nagar Haveli and Daman and Diu', 'code': 'DN'},
            {'name': 'Delhi', 'code': 'DL'},
            {'name': 'Jammu and Kashmir', 'code': 'JK'},
            {'name': 'Ladakh', 'code': 'LA'},
            {'name': 'Lakshadweep', 'code': 'LD'},
            {'name': 'Puducherry', 'code': 'PY'},
        ]
        
        # Create states
        for state_data in states_data:
            state, created = State.objects.get_or_create(
                name=state_data['name'],
                defaults={'code': state_data['code']}
            )
            if created:
                self.stdout.write(f'Created state: {state.name}')
        
        # Sample districts for major states
        districts_data = {
            'Maharashtra': [
                'Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad', 'Solapur', 'Amravati', 'Kolhapur',
                'Sangli', 'Satara', 'Ahmednagar', 'Latur', 'Jalgaon', 'Akola', 'Nanded', 'Raigad'
            ],
            'Delhi': ['Central Delhi', 'East Delhi', 'New Delhi', 'North Delhi', 'North East Delhi', 
                     'North West Delhi', 'Shahdara', 'South Delhi', 'South East Delhi', 'South West Delhi', 'West Delhi'],
            'Karnataka': [
                'Bangalore Urban', 'Bangalore Rural', 'Mysore', 'Hubli-Dharwad', 'Mangalore', 'Belgaum',
                'Gulbarga', 'Davanagere', 'Bellary', 'Bijapur', 'Shimoga', 'Tumkur', 'Raichur'
            ],
            'Tamil Nadu': [
                'Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem', 'Tirunelveli', 'Tiruppur',
                'Vellore', 'Erode', 'Thanjavur', 'Dindigul', 'Cuddalore', 'Kanchipuram'
            ],
            'Gujarat': [
                'Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Bhavnagar', 'Jamnagar', 'Junagadh',
                'Gandhinagar', 'Anand', 'Bharuch', 'Mehsana', 'Patan', 'Porbandar'
            ],
            'Uttar Pradesh': [
                'Lucknow', 'Kanpur', 'Ghaziabad', 'Agra', 'Varanasi', 'Meerut', 'Allahabad', 'Bareilly',
                'Aligarh', 'Moradabad', 'Saharanpur', 'Gorakhpur', 'Noida', 'Firozabad'
            ],
            'West Bengal': [
                'Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri', 'Bardhaman', 'Malda',
                'Baharampur', 'Habra', 'Kharagpur', 'Shantipur', 'Dankuni', 'Dhulian'
            ],
            'Rajasthan': [
                'Jaipur', 'Jodhpur', 'Udaipur', 'Kota', 'Ajmer', 'Bikaner', 'Bhilwara', 'Alwar',
                'Bharatpur', 'Pali', 'Sikar', 'Tonk', 'Kishangarh', 'Beawar'
            ],
            'Punjab': [
                'Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda', 'Mohali', 'Firozpur',
                'Batala', 'Pathankot', 'Moga', 'Abohar', 'Malerkotla', 'Khanna'
            ],
            'Haryana': [
                'Faridabad', 'Gurgaon', 'Panipat', 'Ambala', 'Yamunanagar', 'Rohtak', 'Hisar',
                'Karnal', 'Sonipat', 'Panchkula', 'Bhiwani', 'Sirsa', 'Bahadurgarh'
            ],
            'Madhya Pradesh': [
                'Indore', 'Bhopal', 'Jabalpur', 'Gwalior', 'Ujjain', 'Sagar', 'Dewas', 'Satna',
                'Ratlam', 'Rewa', 'Murwara', 'Singrauli', 'Burhanpur', 'Khandwa'
            ]
        }
        
        # Create districts
        for state_name, district_names in districts_data.items():
            try:
                state = State.objects.get(name=state_name)
                for district_name in district_names:
                    district, created = District.objects.get_or_create(
                        name=district_name,
                        state=state
                    )
                    if created:
                        self.stdout.write(f'Created district: {district.name}, {state.name}')
            except State.DoesNotExist:
                self.stdout.write(f'State {state_name} not found')
        
        # Sample cities for major districts
        cities_data = {
            'Mumbai': ['Andheri', 'Bandra', 'Borivali', 'Dadar', 'Ghatkopar', 'Malad', 'Powai', 'Thane', 'Navi Mumbai'],
            'Pune': ['Aundh', 'Baner', 'Hinjewadi', 'Kothrud', 'Pimpri-Chinchwad', 'Viman Nagar', 'Wakad'],
            'Bangalore Urban': ['Whitefield', 'Koramangala', 'Indiranagar', 'Jayanagar', 'Malleshwaram', 'Rajajinagar', 'HSR Layout'],
            'Chennai': ['T. Nagar', 'Anna Nagar', 'Adyar', 'Velachery', 'Tambaram', 'Chrompet', 'Porur'],
            'Hyderabad': ['Hitech City', 'Gachibowli', 'Kondapur', 'Madhapur', 'Banjara Hills', 'Jubilee Hills'],
            'Ahmedabad': ['Vastrapur', 'Satellite', 'Bopal', 'Maninagar', 'Navrangpura', 'C.G. Road'],
            'Kolkata': ['Salt Lake', 'New Town', 'Ballygunge', 'Park Street', 'Gariahat', 'Howrah'],
            'Jaipur': ['Malviya Nagar', 'Vaishali Nagar', 'Mansarovar', 'Jagatpura', 'Tonk Road'],
        }
        
        # Create cities
        for district_name, city_names in cities_data.items():
            try:
                district = District.objects.get(name=district_name)
                for city_name in city_names:
                    city, created = City.objects.get_or_create(
                        name=city_name,
                        district=district,
                        state=district.state
                    )
                    if created:
                        self.stdout.write(f'Created city: {city.name}, {district.name}')
            except District.DoesNotExist:
                self.stdout.write(f'District {district_name} not found')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated locations!'))
        self.stdout.write(f'Total states: {State.objects.count()}')
        self.stdout.write(f'Total districts: {District.objects.count()}')
        self.stdout.write(f'Total cities: {City.objects.count()}')