from django.contrib import admin
from .models import author,category,article,comment

class authorModel(admin.ModelAdmin):
    list_display = ["__str__"]
    search_fields = ["__str__","details"]
    class Meta:
        Model = author


class articleModel(admin.ModelAdmin):
    list_display = ["__str__","posted_on"]
    search_fields = ['title']
    list_filter = ["posted_on","category"]
    list_per_page = 10
    class Meta:
        Model = article


class categoryModel(admin.ModelAdmin):
    list_display = ["__str__"]
    search_fields = ["__str__"]
    list_per_page = 10
    class Meta:
        Model = category

class commentModel(admin.ModelAdmin):
    list_display = ["__str__"]
    search_fields = ["__str__"]
    list_per_page = 10
    class Meta:
        Model = comment


# Register your models here.
admin.site.register(author,authorModel)
admin.site.register(article,articleModel)
admin.site.register(category,categoryModel)
admin.site.register(comment,commentModel)


