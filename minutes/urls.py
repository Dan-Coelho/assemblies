from django.urls import path
from . import views

urlpatterns = [
    path('atas/<uuid:pk>/', views.MinutesDetailView.as_view(), name='minutes_detail'),
    path('atas/<uuid:pk>/aprovar/', views.MinutesApproveView.as_view(), name='minutes_approve'),
    path('atas/<uuid:pk>/assinar/', views.MinutesSignView.as_view(), name='minutes_sign'),
]
