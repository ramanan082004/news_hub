from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.detail, name='detail'),          # ✅ post_id → pk
    path('post/<int:pk>/download/', views.download_post, name='download_post'),  # ✅ post_id → pk
    path('post/<int:pk>/copy/', views.copy_post, name='copy_post'),
    path('post/', views.some_view, name='post_home'),
   
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('profile/', views.profile_view, name='profile'),
    path('old_url/', views.old_url_redirect, name='old_url'),
    path('new_something_url/', views.new_url_view, name='new_page_url'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
]