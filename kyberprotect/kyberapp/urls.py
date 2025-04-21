from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('lessons/', views.lessons, name='lessons'),
    path('lessons/<int:lesson_id>/', views.lesson_detail,
         name='lesson_detail'),
    path('achievements/', views.achievements, name='achievements'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-faq/', views.admin_faq, name='admin_faq'),
    path('test/<int:test_id>/', views.take_test, name='test_detail'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
