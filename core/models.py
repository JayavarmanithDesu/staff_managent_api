from django.db import models
from django.contrib.auth.models import AbstractUser

# WARNING: Remove this line! It belongs in settings.py
# AUTH_USER_MODEL = 'core.User' 

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
    
    # Optional: Add class Meta for clarity
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
        related_name='users' # Optional related name for Role model
    )
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)

    # --- FIX FOR SYSTEMCHECKERROR (Related Name Clash) ---
    # These fields must be explicitly redefined when using a custom user model
    # to provide unique reverse accessors, resolving the conflict with auth.User.
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
    # ----------------------------------------------------
    
    def __str__(self):
        return self.username