from django.contrib import admin
from django.urls import include, path
from issues.views import (
    CommentViewset,
    ContributorViewset,
    IssueViewset,
    ProjectViewset,
)
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import UsersViewset

router = routers.DefaultRouter()
router.register('projects', ProjectViewset, basename='projects')
router.register('users', UsersViewset, basename='users')

project_router = NestedSimpleRouter(router, 'projects', lookup='projects')
project_router.register('contributors', ContributorViewset, basename='contributors')
project_router.register('issues', IssueViewset, basename="issues")

issue_router = NestedSimpleRouter(project_router, 'issues', lookup='issues')
issue_router.register('comments', CommentViewset, basename="comments")

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/', include(project_router.urls)),
    path('api/', include(issue_router.urls)),
]
