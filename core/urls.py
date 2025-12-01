# In core/urls.py

from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AttendanceViewSet, ScheduleViewSet

router = DefaultRouter()

# Register the ViewSets with the router. 
# The basename is used to generate URL names.
router.register(r'users', UserViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'schedules', ScheduleViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = router.urls