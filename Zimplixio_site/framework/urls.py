from django.urls import path
from . import views

app_name = 'framework'

urlpatterns = [
    path('api/assessment/', views.assessment_view, name='assessment'),
]
