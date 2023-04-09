from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/", include(("julo_mini_wallet.api.urls", "api"), namespace="api_v1")),
    path('api-auth/', include('rest_framework.urls')),
]
