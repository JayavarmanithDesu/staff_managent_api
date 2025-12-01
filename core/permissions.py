# In core/permissions.py

from rest_framework import permissions

# Role IDs: 1=Admin, 2=Manager, 3=Staff

class IsAdmin(permissions.BasePermission):
    """Allows access only to Admin users (Role 1)."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role_id == 1

class IsAdminOrManager(permissions.BasePermission):
    """Allows full access only to Admin (Role 1) or Manager (Role 2) users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role_id in [1, 2]

class CanManageUsers(permissions.BasePermission):
    """
    User endpoint permission:
    - Admin (1) can CRUD (full access).
    - Manager/Staff (2, 3) can only READ/UPDATE their own profile (detail view).
    """
    def has_permission(self, request, view):
        # Admin can do anything
        if request.user.is_authenticated and request.user.role_id == 1:
            return True
        
        # Managers/Staff can only access detail views (retrieve/update their own)
        if view.action in ['retrieve', 'update', 'partial_update']:
             return request.user.is_authenticated
        
        # Block list view (GET all users) for non-admins
        return False
        
    def has_object_permission(self, request, view, obj):
        user = request.user
        # Admin can manage any object
        if user.role_id == 1:
            return True
        
        # Manager/Staff can only read/edit their own object
        return obj == user


class CanAccessAttendance(permissions.BasePermission):
    """
    Attendance endpoint permission:
    - Admin/Manager (1, 2): READ ALL, can POST/PUT for any user (for correction).
    - Staff (3): Only POST (Check-in/out), and only on their own record.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        # Admin/Manager can do anything (List or Detail access)
        if user.role_id in [1, 2]: 
            return True
        
        # Staff (Role 3) can only use POST (Check-in/out). Block them from list GETs.
        if user.role_id == 3 and request.method == 'POST':
            return True
        
        return False
        
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin/Manager can read/edit any attendance object
        if user.role_id in [1, 2]:
            return True
        
        # Staff can only read/edit their OWN record
        return obj.user == user


class CanAccessSchedule(permissions.BasePermission):
    """
    Schedule endpoint permission:
    - Admin/Manager (1, 2): CRUD (manage shifts).
    - Staff (3): Only READ (their own schedule).
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # Admin/Manager can write (POST/PUT/DELETE)
        if user.role_id in [1, 2]:
            return True
        
        # Staff can only read (GET) the list
        if user.role_id == 3 and request.method in permissions.SAFE_METHODS:
            return True

        return False
        
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin/Manager can see/edit any object
        if user.role_id in [1, 2]:
            return True
            
        # Staff can only read (GET) their own schedule object
        if user.role_id == 3 and request.method in permissions.SAFE_METHODS:
            return obj.user == user
        
        return False