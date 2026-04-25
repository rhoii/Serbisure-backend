from rest_framework import serializers
from .models import CustomUser, WorkerProfile, Service, Booking

class WorkerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerProfile
        fields = ['skills', 'bio', 'rating']

class UserSerializer(serializers.ModelSerializer):
    worker_profile = WorkerProfileSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'role', 'phone', 'worker_profile']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'full_name', 'role']
        
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            role=validated_data.get('role', 'homeowner')
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ServiceSerializer(serializers.ModelSerializer):
    provider = UserSerializer(read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'provider', 'name', 'description', 'category', 'price']

class ServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['name', 'description', 'category', 'price']

class BookingSerializer(serializers.ModelSerializer):
    service_details = ServiceSerializer(source='service', read_only=True)
    homeowner_details = UserSerializer(source='homeowner', read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'homeowner', 'homeowner_details', 'service', 'service_details', 'status', 'scheduled_date', 'rating', 'comment']
        read_only_fields = ['homeowner']

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['service', 'scheduled_date']
