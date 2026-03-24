from django.urls import path
from .views import (
    ClientListAPIView,
    ClientCreateAPIView,
    ClientDetailAPIView,
)

urlpatterns = [
    path("", ClientListAPIView.as_view(), name="client-list"),
    path("create/", ClientCreateAPIView.as_view(), name="client-create"),
    path("<int:pk>/", ClientDetailAPIView.as_view(), name="client-detail"),
]