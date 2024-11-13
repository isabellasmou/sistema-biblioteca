from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalogo/', include('catalogo.urls')),
    path('', lambda request: redirect('catalogo/')),  # Redireciona a URL raiz para /catalogo/
]
