from django.urls import path

from dashboard.views import DashboardStatsAPIView

app_name = "dashboard"

urlpatterns = [
    path("", DashboardStatsAPIView.as_view(), name="dashboard-stats"),
]
