from django.urls import path
from statistics_app import views

app_name = "statistics_app"

urlpatterns = [
    path('public', views.workshop_public_stats, name="public"),
    path('team', views.team_stats, name="team"),
    path('team/<int:team_id>', views.team_stats, name="team"),
]
