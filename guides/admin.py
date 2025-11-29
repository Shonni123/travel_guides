from django.contrib import admin
from .models import Country, City, Attraction, Review

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'category', 'average_rating', 'review_count', 'image']
    list_filter = ['country', 'category']
    search_fields = ['name', 'country__name']

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'average_rating', 'review_count', 'image']
    list_filter = ['city__country', 'city']
    search_fields = ['name', 'city__name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'city', 'attraction', 'created_at']
    list_filter = ['rating', 'created_at', 'city', 'attraction']
    search_fields = ['user__username', 'comment', 'city__name', 'attraction__name']
    readonly_fields = ['created_at', 'updated_at']