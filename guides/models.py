from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class City(models.Model):
    CATEGORY_CHOICES = [
        ('history', 'Исторические'),
        ('beach', 'Пляжные'),
        ('modern', 'Мегаполисы'),
        ('nature', 'Природные'),
        ('culture', 'Культурные'),
    ]

    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='cities/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='culture')

    def __str__(self):
        return self.name

    def average_rating(self):
        reviews = self.city_reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0.0

    def review_count(self):
        return self.city_reviews.count()

    def is_favorited_by(self, user):
        """Проверяет, добавлен ли город в избранное пользователем"""
        if user.is_authenticated:
            return self.favorited_by.filter(user=user).exists()
        return False

    def favorite_count(self):
        """Количество пользователей, добавивших город в избранное"""
        return self.favorited_by.count()


class Attraction(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='attractions')
    image = models.ImageField(upload_to='attractions/', blank=True, null=True)

    def __str__(self):
        return self.name

    def average_rating(self):
        reviews = self.attraction_reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0.0

    def review_count(self):
        return self.attraction_reviews.count()


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='city_reviews', null=True, blank=True)
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE, related_name='attraction_reviews', null=True,
                                   blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'city'], name='unique_user_city_review'),
            models.UniqueConstraint(fields=['user', 'attraction'], name='unique_user_attraction_review'),
        ]

    def __str__(self):
        if self.city:
            return f"Отзыв на {self.city.name} от {self.user.username}"
        else:
            return f"Отзыв на {self.attraction.name} от {self.user.username}"

    def save(self, *args, **kwargs):
        # Проверяем, что указан только один объект (город или достопримечательность)
        if not self.city and not self.attraction:
            raise ValueError("Должен быть указан либо город, либо достопримечательность")
        if self.city and self.attraction:
            raise ValueError("Можно указать только город ИЛИ достопримечательность")
        super().save(*args, **kwargs)


class FavoriteCity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'city']  # Один город можно добавить в избранное только один раз
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.city.name}"



