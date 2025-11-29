from django.urls import path
from . import views

app_name = 'guides'

urlpatterns = [
    path('', views.home, name='home'),
    path('city/<int:pk>/', views.city_detail, name='city_detail'),
    path('random/', views.random_city, name='random_city'),
    path('review/<str:object_type>/<int:pk>/', views.add_review, name='add_review'),
    path('review/delete/<int:pk>/', views.delete_review, name='delete_review'),
    path('favorites/toggle/<int:city_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_cities, name='favorite_cities'),

    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),  # Теперь функция существует
    path('profile/', views.profile, name='profile'),
]