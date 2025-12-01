from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import User, Attendance, Schedule
from .serializers import UserSerializer, AttendanceSerializer, ScheduleSerializer
from .permissions import IsAdmin, CanManageUsers, CanAccessAttendance, CanAccessSchedule, IsAdminOrManager # Import Ty's permissions

# --- User ViewSet ---

class UserViewSet(viewsets.ModelViewSet):
    """Provides CRUD operations for User profiles."""
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [CanManageUsers] # Uses the custom permission for user access

# --- Attendance ViewSet ---

class AttendanceViewSet(viewsets.ModelViewSet):
    """Provides API for managing and submitting attendance records."""
    queryset = Attendance.objects.all().order_by('-date', '-check_in_time')
    serializer_class = AttendanceSerializer
    permission_classes = [CanAccessAttendance]

    def get_queryset(self):
        # Staff (Role 3) can only see their own attendance records
        user = self.request.user
        if user.role_id == 3:
            return self.queryset.filter(user=user)
        # Admin/Manager see all records (handled by permission class)
        return self.queryset

    # Custom action for staff to CHECK-IN (POST /attendance/check-in/)
    @action(detail=False, methods=['post'], url_path='check-in')
    def check_in(self, request):
        user = request.user
        today = timezone.localdate()
        
        # Check if user already checked in today
        if Attendance.objects.filter(user=user, date=today).exists():
            return Response({'detail': 'Already checked in today. Please check out.'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Create new attendance record
        Attendance.objects.create(user=user, check_in_time=timezone.now())
        return Response({'detail': 'Check-in successful.'}, status=status.HTTP_201_CREATED)

    # Custom action for staff to CHECK-OUT (POST /attendance/check-out/)
    @action(detail=False, methods=['post'], url_path='check-out')
    def check_out(self, request):
        user = request.user
        today = timezone.localdate()
        
        # Find today's check-in record
        attendance_record = get_object_or_404(
            Attendance, user=user, date=today, check_out_time__isnull=True
        )
        
        # Update record with check-out time
        attendance_record.check_out_time = timezone.now()
        attendance_record.save()
        
        serializer = self.get_serializer(attendance_record)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- Schedule ViewSet ---

class ScheduleViewSet(viewsets.ModelViewSet):
    """Provides API for managing shifts and schedules."""
    queryset = Schedule.objects.all().order_by('shift_date', 'start_time')
    serializer_class = ScheduleSerializer
    permission_classes = [CanAccessSchedule] # Uses the custom permission for schedule access

    def get_queryset(self):
        # Staff (Role 3) can only see their own schedules
        user = self.request.user
        if user.role_id == 3:
            return self.queryset.filter(user=user)
        # Admin/Manager see all schedules
        return self.queryset
        
    # Optional: Customize create method to assign the user_id from the serializer
    # def create(self, request, *args, **kwargs):
    #     # Logic for handling user_id input from serializer if needed
    #     return super().create(request, *args, **kwargs)