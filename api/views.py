from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from .permissions import IsServiceWorker, IsServiceProviderOrReadOnly, IsHomeowner, IsServiceWorkerOrReadOnly
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import CustomUser, WorkerProfile, Service, Booking
from .serializers import (
    UserSerializer, LoginSerializer, RegisterSerializer, 
    ServiceSerializer, BookingSerializer, WorkerProfileSerializer
)
import logging

# Module 3: Debugging/Logging Configuration
logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        logger.info("New registration attempt detected.")
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create worker profile if role is service_worker
            if user.role == 'service_worker':
                WorkerProfile.objects.get_or_create(user=user)
            
            # Create Token for the new user
            token, created = Token.objects.get_or_create(user=user)
                
            return Response({
                "status": "success", 
                "data": {
                    "user": UserSerializer(user).data,
                    "token": token.key
                }
            }, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        logger.info("Manual login attempt.")
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(request, username=email, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "status": "success",
                    "data": {
                        "token": token.key,
                        "user": UserSerializer(user).data
                    }
                }, status=status.HTTP_200_OK)
            return Response({"status": "error", "message": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class ServiceListView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsServiceWorkerOrReadOnly] # Module 3: Anyone can View, Only Workers can Create

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

    def perform_create(self, serializer):
        # Automatically set the provider to the logged in worker
        serializer.save(provider=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)

class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsServiceProviderOrReadOnly] # Module 3: Anyone can View, Only Owner can Edit/Delete

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": "success", 
            "message": "Service deleted successfully"
        }, status=status.HTTP_200_OK)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Homeowners see bookings they made; Workers see bookings where they are the provider
        user = self.request.user
        if user.role == 'service_worker':
            return Booking.objects.filter(service__provider=user)
        return Booking.objects.filter(homeowner=user)
        
    def perform_create(self, serializer):
        # Automatically tie the booking to the logged in user
        serializer.save(homeowner=self.request.user)

    def create(self, request, *args, **kwargs):
        # Only Homeowners can initiate a booking
        if request.user.role != 'homeowner':
            return Response({
                "status": "error", 
                "message": "Only homeowners can create bookings."
            }, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": "success", 
            "message": "Booking deleted successfully"
        }, status=status.HTTP_200_OK)

class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"status": "success", "data": serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"status": "success", "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"status": "success", "message": "Profile deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class GoogleSyncView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        try:
            email = request.data.get('email')
            logger.info(f"Google sync requested for: {email}")
            
            if not email:
                return Response({"status": "error", "message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
                
            # 1. Attempt to find existing user
            user = CustomUser.objects.filter(email=email).first()
            
            if not user:
                # 2. If not found, check if a role was provided for registration
                role = request.data.get('role')
                if not role:
                    # No user and no role = Need to redirect to role selection
                    return Response({
                        "status": "error",
                        "message": "User not found. Registration required.",
                        "code": "user_not_found"
                    }, status=status.HTTP_404_NOT_FOUND)

                # Proceed with registration (Shadow Profile)
                password = request.data.get('password')
                if not password:
                    from django.utils.crypto import get_random_string
                    password = get_random_string(32)
                
                serializer = RegisterSerializer(data={
                    'email': email,
                    'password': password,
                    'full_name': request.data.get('full_name', email.split('@')[0]),
                    'role': role
                })
                if serializer.is_valid():
                    user = serializer.save()
                else:
                    return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. Ensure worker profile exists if role is service_worker
            if user.role == 'service_worker':
                WorkerProfile.objects.get_or_create(user=user)
                
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                "status": "success",
                "data": {
                    "user": UserSerializer(user).data,
                    "token": token.key
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Server Error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] # Module 3: Secure Audit/Admin View

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "status": "success", 
            "message": "User account deleted successfully"
        }, status=status.HTTP_200_OK)

class WorkerProfileViewSet(viewsets.ModelViewSet):
    queryset = WorkerProfile.objects.all()
    serializer_class = WorkerProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Workers can only manage their own profile metadata
        if getattr(self, 'action', None) in ['update', 'partial_update', 'destroy']:
            return WorkerProfile.objects.filter(user=self.request.user)
        return WorkerProfile.objects.all()
