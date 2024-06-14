from django.urls import path
from .views import wake_on_lan_page, wake_and_check, check_host_up, receive_data

urlpatterns = [
    path('', wake_on_lan_page, name='wake_on_lan_page'),
    path('api/wake_and_check/', wake_and_check, name='wake_and_check'),
    path('api/check_host_up/', check_host_up, name='check_host_up'),
    path('api/receive_data/', receive_data, name='receive_data'),
]
