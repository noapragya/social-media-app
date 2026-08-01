from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from userauth import views as userauth_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication & Core
    path('', userauth_views.home, name='home'),
    path('signup/', userauth_views.signup, name='signup'),
    path('login/', userauth_views.login_view, name='login'), 
    path('logout/', userauth_views.logout_view, name='logout'),
    
    # Feature Routes
    path('explore/', userauth_views.explore, name='explore'),
    path('upload/', userauth_views.upload, name='upload'),
    path('like-post/<str:post_id>/', userauth_views.like_post, name='like-post'),
    path('notifications/', userauth_views.notifications_view, name='notifications'),
    path('search/', userauth_views.search, name='search'),
    path('profile/<str:pk>/', userauth_views.profile, name='profile'),
    path('edit-profile/', userauth_views.edit_profile, name='edit-profile'),
    path('delete-post/<str:post_id>/', userauth_views.delete_post, name='delete-post'),

    # Messaging Routes (Fixes 'inbox' and 'chat-detail' errors)
    path('inbox/', userauth_views.inbox, name='inbox'),
    path('chat/<str:username>/', userauth_views.chat_detail, name='chat-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)