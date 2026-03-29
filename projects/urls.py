from django.urls import path

from .views import (
    AssignProjectMembersAPIView,
    MyProjectsAPIView,
    ProjectDetailAPIView,
    ProjectListCreateAPIView,
)

app_name = "projects"

urlpatterns = [
    path("", ProjectListCreateAPIView.as_view(), name="project-list-create"),
    path("my-projects/", MyProjectsAPIView.as_view(), name="my-projects"),
    path("<int:pk>/", ProjectDetailAPIView.as_view(), name="project-detail"),
    path(
        "<int:pk>/assign-members/",
        AssignProjectMembersAPIView.as_view(),
        name="assign-members",
    ),
]
