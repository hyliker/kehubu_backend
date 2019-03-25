from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path

router = DefaultRouter()
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'group', views.GroupViewSet, basename='group')
router.register(r'member', views.MemberViewSet, basename='member')
urlpatterns = router.urls
urlpatterns += [
    path('joingroup/', views.JoinGroupView.as_view(), name='JoinGroup'),
]