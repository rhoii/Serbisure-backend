from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import CustomUser, Service, Booking

class SerbiSureAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a test service worker
        self.user = CustomUser.objects.create_user(
            username="worker@example.com",
            email="worker@example.com",
            password="password123",
            full_name="Test Worker",
            role="service_worker"
        )
        # Auth credentials for the client
        from rest_framework.authtoken.models import Token
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Create test services for pagination check
        for i in range(15):
            Service.objects.create(
                provider=self.user,
                name=f"Service {i}",
                description="Test Description",
                category="Maintenance",
                price=100.00
            )

    def test_api_v1_versioning(self):
        """Activity A: Verify that the API is accessible via /api/v1/"""
        url = "/api/v1/services/"
        # Services GET requires authenticated Service Worker in current system views.py
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_global_pagination(self):
        """Activity A: Verify that results are paginated (PAGE_SIZE=10)"""
        url = reverse('service-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify pagination structure
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('results', response.data)
        
        # Verify page size
        self.assertEqual(len(response.data['results']), 10)
        self.assertEqual(response.data['count'], 15)

    def test_authentication_required(self):
        """Activity D: Verify authentication requirement for private endpoints"""
        self.client.credentials() # Reset token
        url = reverse('booking-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_and_access(self):
        """Activity D: Verify login and authenticated access"""
        self.client.credentials() # Reset token
        # Login
        url = reverse('login')
        response = self.client.post(url, {
            "email": "worker@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Fix: The token is inside the 'data' envelope
        token = response.data['data']['token']
        
        # Access with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        url = reverse('booking-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_service_crud_flow(self):
        """Item 11: Verify End-to-End CRUD flow (Create, Retrieve, Update, Delete)"""
        # 1. CREATE
        url = reverse('service-list')
        create_res = self.client.post(url, {
            "name": "Automated Test Service",
            "description": "Testing CRUD",
            "category": "Test",
            "price": "99.99"
        })
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        # Fix: The created data is inside the 'data' envelope
        service_id = create_res.data['data']['id']

        # 2. RETRIEVE
        url = reverse('service-detail', args=[service_id])
        get_res = self.client.get(url)
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        # Fix: Default retrieve sometimes raw, but let's check view
        # ServiceDetailView uses raw RetrieveUpdateDestroyAPIView usually
        # but my test suite should be consistent.
        data = get_res.data
        name = data.get('name') or data.get('data', {}).get('name')
        self.assertEqual(name, "Automated Test Service")

        # 3. UPDATE
        update_res = self.client.patch(url, {
            "price": "150.00"
        })
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)
        
        # 4. DELETE
        delete_res = self.client.delete(url)
        # My ServiceDetailView destroy uses custom Response too
        self.assertEqual(delete_res.status_code, status.HTTP_200_OK)
        
        # Verify it's gone
        final_get = self.client.get(url)
        self.assertEqual(final_get.status_code, status.HTTP_404_NOT_FOUND)
