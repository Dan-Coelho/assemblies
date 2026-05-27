from django.urls import path
from . import views

urlpatterns = [
    # Organization URLs
    path('organizations/', views.OrganizationListView.as_view(), name='organization_list'),
    path('organizations/create/', views.OrganizationCreateView.as_view(), name='organization_create'),
    path('organizations/<uuid:pk>/', views.OrganizationDetailView.as_view(), name='organization_detail'),
    path('organizations/<uuid:pk>/edit/', views.OrganizationUpdateView.as_view(), name='organization_update'),

    # Member URLs (aninhadas por organização)
    path('organizations/<uuid:org_pk>/members/', views.MemberListView.as_view(), name='member_list'),
    path('organizations/<uuid:org_pk>/members/create/', views.MemberCreateView.as_view(), name='member_create'),
    path('organizations/<uuid:org_pk>/members/<uuid:pk>/edit/', views.MemberUpdateView.as_view(), name='member_update'),
]
