from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_member, name='add_member'),
    path('', views.member_list, name='member_list'),
    path('scan/', views.scan_face, name='scan_face'),
    path('delete/<int:member_id>/', views.delete_member, name='delete_member'),
]

