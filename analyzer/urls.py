from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import app_list, create_item,  delete_item ,register,edit_item

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='analyzer/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('apps/', app_list, name='app_list'),
    path('create/', create_item, name='create_item'),  # URL for creating an app
    path('delete_item/<int:app_id>/', delete_item, name='delete_item'),
    path('edit_item/<int:app_id>/', edit_item, name='edit_item'),
    path('register/', register, name='register'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

