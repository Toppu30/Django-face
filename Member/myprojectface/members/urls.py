from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_member, name='add_member'),
    path('member_list', views.member_list, name='member_list'),
    path('scan/', views.scan_face, name='scan_face'),
    path('delete/<int:member_id>/', views.delete_member, name='delete_member'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('check_faces/', views.check_faces, name='check_faces'),
    path('edit/<int:member_id>/', views.edit_member, name='edit_member'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.auth_views.LogoutView.as_view(), name='logout'),
    path('', views.home, name='home'),
    path('user_list/', views.user_list, name='user_list'),
    path('user/<int:user_id>/', views.user_edit, name='user_edit'),
]

