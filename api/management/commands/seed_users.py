from django.core.management.base import BaseCommand
from api.models import CustomUser, WorkerProfile, Service, Booking
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Seeds the database with a standard set of test users (Homeowner, Worker, Admin)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding standard test users...')
        
        users_data = [
            {
                "email": "admin@serbisure.com",
                "username": "admin@serbisure.com",
                "full_name": "System Administrator",
                "role": "homeowner", # Admin is technically an owner
                "password": "adminpassword123",
                "is_staff": True,
                "is_superuser": True
            },
            {
                "email": "home@serbisure.com",
                "username": "home@serbisure.com",
                "full_name": "Maria Homeowner",
                "role": "homeowner",
                "password": "homepassword123"
            },
            {
                "email": "worker@serbisure.com",
                "username": "worker@serbisure.com",
                "full_name": "Pedro Worker",
                "role": "service_worker",
                "password": "workerpassword123"
            }
        ]

        # 1. Create Users
        for data in users_data:
            password = data.pop('password')
            user, created = CustomUser.objects.get_or_create(
                email=data['email'],
                defaults=data
            )
            if created:
                user.set_password(password)
                user.save()

        # 2. Get the specific test users
        try:
            worker = CustomUser.objects.get(email="worker@serbisure.com")
            maria = CustomUser.objects.get(email="home@serbisure.com")
            
            # 3. Create a Variety of Services for Pedro
            services_data = [
                {
                    "name": "General House Cleaning",
                    "description": "Professional cleaning service for your entire home.",
                    "category": "Maintenance",
                    "price": 500.00
                },
                {
                    "name": "Aircon Deep Cleaning",
                    "description": "Full chemical cleaning for split or window-type AC units.",
                    "category": "Home Service",
                    "price": 1200.00
                },
                {
                    "name": "Emergency Plumbing",
                    "description": "Fixing leaks, toilets, and pipe burst repairs.",
                    "category": "Maintenance",
                    "price": 800.00
                },
                {
                    "name": "Basic Electrical Repair",
                    "description": "Fixing sockets, light fixtures, and breaker issues.",
                    "category": "Maintenance",
                    "price": 750.00
                }
            ]

            created_services = []
            for s_data in services_data:
                service, created = Service.objects.get_or_create(
                    name=s_data['name'],
                    provider=worker,
                    defaults=s_data
                )
                created_services.append(service)

            # 4. Create Multiple Bookings for Maria
            bookings_data = [
                {
                    "service": created_services[0], # Cleaning
                    "status": "pending",
                    "delta_days": 2
                },
                {
                    "service": created_services[1], # Aircon
                    "status": "confirmed",
                    "delta_days": 5
                },
                {
                    "service": created_services[2], # Plumbing
                    "status": "completed",
                    "delta_days": -2 # Completed in the past
                }
            ]

            for b_data in bookings_data:
                Booking.objects.get_or_create(
                    homeowner=maria,
                    service=b_data['service'],
                    status=b_data['status'],
                    defaults={
                        "scheduled_date": timezone.now().date() + datetime.timedelta(days=b_data['delta_days'])
                    }
                )

            self.stdout.write(self.style.SUCCESS('Successfully seeded multiple services and bookings!'))

        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR('Required test users (home/worker) not found.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding data: {e}"))

        self.stdout.write(self.style.SUCCESS('Seeding process complete.'))
