from django.contrib import admin
from .models import Category, Brand, Product, Attribute, AttributeValue


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'brand', 'price', 'quantity')
    list_filter = ('category', 'brand')
    search_fields = ('title', 'description')
    inlines = [AttributeValueInline]


admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product, ProductAdmin)
admin.site.register(Attribute)
admin.site.register(AttributeValue)
