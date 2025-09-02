from django.core.management.base import BaseCommand
from listings.models import State, District


INDIA_STATES = [
    'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Goa','Gujarat','Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal','Andaman and Nicobar Islands','Chandigarh','Dadra and Nagar Haveli and Daman and Diu','Delhi','Jammu and Kashmir','Ladakh','Lakshadweep','Puducherry'
]


class Command(BaseCommand):
    help = 'Seed India states (districts can be loaded separately)'

    def handle(self, *args, **options):
        created = 0
        for name in INDIA_STATES:
            _, was_created = State.objects.get_or_create(name=name)
            created += 1 if was_created else 0
        self.stdout.write(self.style.SUCCESS(f'Seeded states. New: {created}, Total: {State.objects.count()}'))
