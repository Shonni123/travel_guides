from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
import random
from .models import City, Review
from .forms import ReviewForm

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
import random
from .models import City

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import FavoriteCity


@login_required
@login_required
def toggle_favorite(request, city_id):
    """Добавить/удалить город из избранного"""
    city = get_object_or_404(City, id=city_id)

    if request.method == 'POST':
        favorite, created = FavoriteCity.objects.get_or_create(
            user=request.user,
            city=city
        )

        if not created:
            # Если уже был в избранном - удаляем
            favorite.delete()
            is_favorited = False
        else:
            is_favorited = True

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX запрос
            return JsonResponse({
                'is_favorited': is_favorited,
                'favorite_count': city.favorite_count()
            })

    return redirect('guides:city_detail', pk=city_id)


from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('guides:home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'guides/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'guides/login.html'

    def get_success_url(self):
        messages.success(self.request, f'Добро пожаловать, {self.request.user.username}!')
        return super().get_success_url()


def profile(request):
    return render(request, 'guides/profile.html')
from django.contrib.auth.views import LogoutView as DjangoLogoutView

from django.contrib.auth.views import LogoutView as DjangoLogoutView

class CustomLogoutView(DjangoLogoutView):
    def get_next_page(self):
        messages.success(self.request, 'Вы успешно вышли из аккаунта')
        return super().get_next_page()

@login_required
def favorite_cities(request):
    """Страница с избранными городами пользователя"""
    favorites = FavoriteCity.objects.filter(user=request.user).select_related('city')
    return render(request, 'guides/favorite_cities.html', {
        'favorites': favorites
    })


def home(request):
    cities = City.objects.all()

    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    if search_query:
        cities = cities.filter(
            Q(name__icontains=search_query) |
            Q(country__name__icontains=search_query)
        )
        if cities.count() == 1:
            return redirect('guides:city_detail', pk=cities.first().pk)

    if category_filter:
        cities = cities.filter(category=category_filter)

    return render(request, 'guides/home.html', {
        'cities': cities,
        'search_query': search_query,
        'category_filter': category_filter  # УБЕДИТЕСЬ ЧТО ТУТ НЕТ ЛИШНИХ ЗАПЯТЫХ ИЛИ СКОБОК
    })


def city_detail(request, pk):
    city = get_object_or_404(City, pk=pk)
    attractions = city.attractions.all()

    # Получаем отзывы для города
    reviews = city.city_reviews.all()[:5]

    # Проверяем, оставлял ли пользователь отзыв
    user_review = None
    review_form = None

    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, city=city).first()
        if not user_review:
            review_form = ReviewForm()

    return render(request, 'guides/city_detail.html', {
        'city': city,
        'attractions': attractions,
        'reviews': reviews,
        'review_form': review_form,
        'user_review': user_review
    })


def random_city(request):
    cities = list(City.objects.all())
    if cities:
        city = random.choice(cities)
        attractions = city.attractions.all()
        return render(request, 'guides/random_city.html', {
            'city': city,
            'attractions': attractions
        })
    return render(request, 'guides/random_city.html', {'city': None})


@login_required
def add_review(request, object_type, pk):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user

            if object_type == 'city':
                review.city = get_object_or_404(City, pk=pk)
                redirect_url = 'guides:city_detail'
                redirect_pk = pk
            elif object_type == 'attraction':
                from .models import Attraction
                attraction = get_object_or_404(Attraction, pk=pk)
                review.attraction = attraction
                redirect_url = 'guides:city_detail'
                redirect_pk = attraction.city.pk

            try:
                review.save()
                messages.success(request, 'Ваш отзыв успешно добавлен!')
            except Exception as e:
                messages.error(request, 'Вы уже оставляли отзыв на этот объект')

            return redirect(redirect_url, pk=redirect_pk)

    return redirect('guides:home')


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)

    # Сохраняем ID для редиректа
    if review.city:
        redirect_pk = review.city.pk
    elif review.attraction:
        redirect_pk = review.attraction.city.pk
    else:
        redirect_pk = None

    review.delete()
    messages.success(request, 'Отзыв удален')

    if redirect_pk:
        return redirect('guides:city_detail', pk=redirect_pk)
    return redirect('guides:home')
def custom_logout(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из аккаунта')
    return redirect('guides:home')