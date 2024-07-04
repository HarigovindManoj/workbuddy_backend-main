from django.urls import path
from .views import SignupView, LoginView, LogoutView, AddUserDetailView, UserDetailView

app_name = 'users'

urlpatterns = [
    path('api/signup/', SignupView.as_view(), name='signup'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/add-user-detail/<str:email>/', AddUserDetailView.as_view(), name='add-user-detail'),
    path('api/user-detail/', UserDetailView.as_view(), name='user-detail'),
]