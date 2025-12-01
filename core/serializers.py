from rest_framework import serializers
from .models import User, Attendance, Schedule, Role

# --- User Serializers ---

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name')
        
class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True) # Read-only nested representation
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), source='role', write_only=True, required=False
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'phone_number', 'address', 'role', 'role_id')
        read_only_fields = ('email',) # Assuming email is not changed frequently
        
    def create(self, validated_data):
        # Admin is responsible for creating users, password needs to be set
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

# --- Attendance Serializers ---

class AttendanceSerializer(serializers.ModelSerializer):
    # Display the username instead of just the user ID for readability
    user = serializers.CharField(source='user.username', read_only=True) 

    class Meta:
        model = Attendance
        # We exclude check_out_time for the initial POST request (check-in)
        fields = ('id', 'user', 'check_in_time', 'check_out_time', 'date', 'duration')
        read_only_fields = ('date', 'duration')
        
# --- Schedule Serializers ---

class ScheduleSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = Schedule
        fields = ('id', 'user', 'user_id', 'shift_date', 'start_time', 'end_time', 'notes')