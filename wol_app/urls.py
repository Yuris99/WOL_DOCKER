from django.urls import path
from .views import wake_and_check, receive_data, check_host_up, wake_on_lan_page

urlpatterns = [
    path('', wake_on_lan_page, name='wake_on_lan_page'),
    path('api/wake_and_check/', wake_and_check, name='wake_and_check'),
    path('api/receive_data/', receive_data, name='receive_data'),
    path('api/check_host_up/', check_host_up, name='check_host_up'),
]
