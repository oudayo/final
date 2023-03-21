from django.urls import path
from .views import *

urlpatterns = [

    path('google_search/', SearchView().as_view(), name='search'),

]