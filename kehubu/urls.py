from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path

router = DefaultRouter()
router.register(r'profile', views.ProfileViewSet, basename='profile')
router.register(r'group', views.GroupViewSet, basename='group')
router.register(r'member', views.MemberViewSet, basename='member')
router.register(r'memberinviter', views.MemberInviterViewSet, basename='memberinviter')
router.register(r'memberuser', views.MemberUserViewSet, basename='memberuser')
router.register(r'groupmemberrank', views.GroupMemberRankViewSet, basename='groupmemberrank')
urlpatterns = router.urls
urlpatterns += [
    path('joingroup/', views.JoinGroupView.as_view(), name='JoinGroup'),
]