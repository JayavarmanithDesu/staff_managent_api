from django.db import models
from django.contrib.auth.models import AbstractUser

# --- Core RBAC Models ---

class Role(models.Model):
    # Choices map to your RBAC matrix
    ROLE_CHOICES = (
        (1, 'Admin'),
        (2, 'Manager'),
        (3, 'Staff'),
    )
    
    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Roles"


class User(AbstractUser):
    # The default fields (username, email, password, etc.) are inherited.
    
    # Custom fields:
    role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users'
    )
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)

    # FIX for SystemCheckError: Must redefine groups and user_permissions 
    # with unique related_names when inheriting AbstractUser.
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_user_set', 
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_user_permissions_set', 
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    def __str__(self):
        return self.username

# --- Operational Models ---

class Attendance(models.Model):
    # Foreign key uses a string 'User' because the model is defined below or in the same file
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='attendance_records') 
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True) # Automatically set when the record is created

    class Meta:
        verbose_name_plural = "Attendance Records"
        # Prevents a user from checking in multiple times on the same date
        unique_together = ('user', 'date') 

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    @property
    def duration(self):
        # Calculates time difference only if both times are recorded
        if self.check_in_time and self.check_out_time:
            return self.check_out_time - self.check_in_time
        return None


class Schedule(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='schedules')
    shift_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Schedules"
        # Ensures no staff member is double-booked for the same date/time
        unique_together = ('user', 'shift_date', 'start_time')

    def __str__(self):
        return f"{self.user.username}'s shift on {self.shift_date} ({self.start_time} to {self.end_time})"