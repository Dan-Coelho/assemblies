from django.urls import path
from . import views

urlpatterns = [
    path('assembleias/', views.AssemblyListView.as_view(), name='assembly_list'),
    path('assembleias/nova/', views.AssemblyCreateView.as_view(), name='assembly_create'),
    path('assembleias/<uuid:pk>/', views.AssemblyDetailView.as_view(), name='assembly_detail'),
    path('assembleias/<uuid:pk>/editar/', views.AssemblyUpdateView.as_view(), name='assembly_update'),
    path('assembleias/<uuid:pk>/iniciar/', views.AssemblyStartView.as_view(), name='assembly_start'),
    path('assembleias/<uuid:pk>/encerrar/', views.AssemblyCloseView.as_view(), name='assembly_close'),
    path('assembleias/<uuid:pk>/convocacoes/nova/', views.ConvocationCreateView.as_view(), name='convocation_create'),
    path('assembleias/<uuid:pk>/procuracoes/nova/', views.ProxyCreateView.as_view(), name='proxy_create'),
    path('assembleias/<uuid:pk>/credenciamento/novo/', views.CredentialCreateView.as_view(), name='credential_create'),
]
