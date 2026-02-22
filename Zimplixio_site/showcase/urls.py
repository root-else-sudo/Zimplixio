from django.urls import path
from . import views

app_name = 'showcase'

urlpatterns = [
    path('', views.ShowcaseGalleryView.as_view(), name='gallery'),
    path('<slug:slug>/', views.ShowcaseDetailView.as_view(), name='detail'),
]
