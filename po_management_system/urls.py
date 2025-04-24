"""
URL configuration for po_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from dj_rest_auth.views import LoginView, LogoutView
from rest_framework_simplejwt.views import TokenVerifyView
from dj_rest_auth.jwt_auth import get_refresh_view

from apps.product.views import ProductViewSet
from apps.purchase.views import PurchaseOrderViewSet, PurchaseOrderListView
from apps.supplier.views import SupplierViewSet

router = DefaultRouter()

router.register(r'supplier', SupplierViewSet)
router.register(r'product', ProductViewSet)
router.register(r'purchase', PurchaseOrderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', LoginView.as_view(), name='rest_login'),
    path('api/logout/', LogoutView.as_view(), name='rest_logout'),
    path('api/token/refresh/', get_refresh_view().as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', TemplateView.as_view(template_name='login.html'), name='login_page'),
    path('dashboard/', PurchaseOrderListView.as_view(), name='dashboard'),

]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]