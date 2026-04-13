from django.core.management.base import BaseCommand
from api.models import Service

class Command(BaseCommand):
    help = 'Seeds the database with professional services for demo purposes'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding professional services...')
        
        services_data = [
            {
                "name": "General Plumbing",
                "description": "Fixing leaks, pipes, faucets, and toilets.",
                "category": "Plumbing",
                "price": 350.00
            },
            {
                "name": "Electrical Repair",
                "description": "Wiring, outlets, circuit breakers, and electrical troubleshooting.",
                "category": "Electrical",
                "price": 450.00
            },
            {
                "name": "Standard House Cleaning",
                "description": "Mopping, dusting, vacuuming, and general tidying up.",
                "category": "Cleaning",
                "price": 250.00
            },
            {
                "name": "Deep Cleaning",
                "description": "Intensive cleaning for move-ins, move-outs, or post-construction.",
                "category": "Cleaning",
                "price": 600.00
            },
            {
                "name": "Garden Maintenance",
                "description": "Lawn mowing, pruning, weeding, and garden cleanup.",
                "category": "Gardening",
                "price": 300.00
            },
            {
                "name": "Home Painting",
                "description": "Interior and exterior wall painting and surface preparation.",
                "category": "Renovation",
                "price": 500.00
            },
            {
                "name": "AC Cleaning & Maintenance",
                "description": "Filter cleaning and general maintenance for split and window type units.",
                "category": "Maintenance",
                "price": 400.00
            },
            {
                "name": "Furniture Assembly",
                "description": "Putting together wardrobes, beds, desks, and other flat-pack furniture.",
                "category": "Handyman",
                "price": 300.00
            },
            {
                "name": "Pest Control",
                "description": "General pest control for ants, termites, and roaches.",
                "category": "Sanitation",
                "price": 1200.00
            },
            {
                "name": "Roof Leak Repair",
                "description": "Sealing and fixing damaged roof tiles and gutter issues.",
                "category": "Renovation",
                "price": 850.00
            }
        ]

        for data in services_data:
            # Update if exists, otherwise create
            service, created = Service.objects.update_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created service: {service.name}'))
            else:
                self.stdout.write(f'Updated service: {service.name}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded all services!'))
