from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import CustomUser, WorkerProfile, Service, Booking
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer, ServiceSerializer, BookingSerializer
import logging

# Module 3: Debugging/Logging Configuration
logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
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

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

# ... (other code)

class ServiceListView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # Module 3: Allow Read, require Auth for Create

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)

class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # Module 3: Allow Read, require Auth for Update/Delete

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own bookings
        return Booking.objects.filter(homeowner=self.request.user)
        
    def perform_create(self, serializer):
        # Automatically tie the booking to the logged in user
        serializer.save(homeowner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED, headers=headers)
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

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

class WorkerProfileViewSet(viewsets.ModelViewSet):
    queryset = WorkerProfile.objects.all()
    serializer_class = WorkerProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Workers can only manage their own profile metadata
        if getattr(self, 'action', None) in ['update', 'partial_update', 'destroy']:
            return WorkerProfile.objects.filter(user=self.request.user)
        return WorkerProfile.objects.all()
