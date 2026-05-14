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
from user.views import UsersViewset

router = routers.DefaultRouter()
router.register('project', ProjectViewset, basename='projects')
router.register('user', UsersViewset, basename='users')

project_router = NestedSimpleRouter(router, 'project', lookup='project')
project_router.register('contributor', ContributorViewset, basename='contributors')
project_router.register('issue', IssueViewset, basename="issues")

issue_router = NestedSimpleRouter(project_router, 'issue', lookup='issue')
issue_router.register('comment', CommentViewset, basename="comments")

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    path('api/', include(project_router.urls)),
    path('api/', include(issue_router.urls)),
]
