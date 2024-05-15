from django.urls import path

from .views import *

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('addpage/', AddPost.as_view(), name='add_page'),
    path('contact/', ContactFormView.as_view(), name='contact'),
    path('contact/', ContactFormView.as_view(), name='contact'),
    path('post/<slug:slug>/', ShowPost.as_view(), name='post'),
    path('update/<slug:slug>/', UpdatePost.as_view(), name='update_post'),
    path('delete/<slug:slug>/', DeletePost.as_view(), name='delete_post'),
    path('category/<slug:cat_slug>/', BikeCategory.as_view(), name='category'),
    path('tag/<slug:tag_slug>/', BikeTags.as_view(), name='tag'),
    path('reader_like/<int:pk>/', reader_like, name='reader_like'),
]
