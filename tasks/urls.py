from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('add/', views.task_create, name='task_create'),
    path('<int:pk>/toggle/', views.task_toggle_done, name='task_toggle_done'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/photo/', views.update_photo_view, name='update_photo'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
path('reset-password/<str:uidb64>/<str:token>/', views.reset_password_view, name='reset_password'),
]