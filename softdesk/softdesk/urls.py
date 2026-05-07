from django.contrib import admin
from django.urls import include, path
from issues.views import ContributorViewset, ProjectViewset
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from user.views import UsersViewset

router = routers.SimpleRouter()
router.register('user', UsersViewset, basename='users')
router.register('contributor', ContributorViewset, basename='contributors')
router.register('project', ProjectViewset, basename='projects')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
]
