from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import CustomUser, WorkerProfile, Service, Booking
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer, ServiceSerializer, BookingSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
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

class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"status": "success", "data": serializer.data})

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

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({"status": "success", "data": serializer.data})

class GoogleSyncView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email')
            
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
