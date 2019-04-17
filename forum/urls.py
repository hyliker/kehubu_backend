from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path

router = DefaultRouter()
router.register(r'category', views.CategoryViewSet, basename='category')
router.register(r'topic', views.TopicViewSet, basename='topic')
router.register(r'post', views.PostViewSet, basename='post')
router.register(r'attachment', views.AttachmentViewSet, basename='attachment')
urlpatterns = router.urls