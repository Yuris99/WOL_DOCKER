from django.urls import path
from .views import wake_on_lan_page, wake_and_check, execute_cmd, check_host_up, get_cmd_files

urlpatterns = [
    path('', wake_on_lan_page, name='wake_on_lan_page'),
    path('api/wake_and_check/', wake_and_check, name='wake_and_check'),
    path('api/check_host_up/', check_host_up, name='check_host_up'),
    path('api/get_cmd_files/', get_cmd_files, name='get_cmd_files'),
    path('api/execute_cmd/', execute_cmd, name='execute_cmd'),
]
