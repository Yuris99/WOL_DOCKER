from django.urls import path
from .views import send_wol_packet

urlpatterns = [
    path('send-wol-packet/', send_wol_packet, name='send_wol_packet'),
]
