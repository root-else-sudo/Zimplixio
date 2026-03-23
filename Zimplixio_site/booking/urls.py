from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.BookCallView.as_view(), name='book'),
    path('success/', views.BookingSuccessView.as_view(), name='booking_success'),
    path('slots/', views.available_slots_view, name='slots'),
    path('available-days/', views.available_days_view, name='available_days'),
]
