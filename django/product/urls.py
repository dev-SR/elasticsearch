
# default router

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, BrandViewSet, AttributeViewSet, AttributeValueViewSet, CustomView


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'products', ProductViewSet)
router.register(r'attributes', AttributeViewSet)
router.register(r'attribute-values', AttributeValueViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('test/', CustomView.as_view(), name='CustomView'),

]
