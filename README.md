# Django Search Vector Model Mixin

This Django app provides a mixin for adding a search vector field to a model.

App supports Multilingual Search Vector fields, which depend on the settings.LANGUAGES.

This functionality is useful for a combination with django-modeltranslation, 
because django-modeltranslation provides a model field for each language and doesn't support multilingual SearchVectorField.

This app is focused on PostgreSQL and GinIndex.

## Installation

With PIP: 

```bash
pip install django-search-vector-model-mixin
```

With Poetry:

```bash
poetry add django-search-vector-model-mixin
```

## Usage

### Add app to INSTALLED_APPS

```python
INSTALLED_APPS = [
    ...
    'django_search-vector-model-mixin'
]
```

### Add mixin to your model

#### Example with single search_vector field

The following example shows how to add a search vector field to a model.

```python
from django_search_vector_model_mixin.models import SearchVectorModelMixin

class MyModel(SearchVectorModelMixin, models.Model):
    search_fields = ['title', 'description'] # write fields, which will be added to search vector
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # inherit from SearchVectorModelMixin.Meta for support of GinIndex
    class Meta(SearchVectorModelMixin.Meta):
        pass
```

In this case, the search vector field will be named 'search_vector'.

#### Example with multilingual search_vector field

The following example shows how to add a search vector field to a model with multilingual support.

```python
from django_search_vector_model_mixin.models import MultilingualSearchVectorModelMixin

class MyModel(MultilingualSearchVectorModelMixin, models.Model):
    search_fields = ['title', 'description'] # write fields, which will be added to search vector
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # inherit from SearchVectorModelMixin.Meta for support of GinIndex
    class Meta(MultilingualSearchVectorModelMixin.Meta):
        pass
```

**MultilingualSearchVectorModelMixin** works with django-modeltranslation.

It means you should configure translator for selected search_fields by django-modeltranslation documentation.

For example:

**translator.py**
```python
from modeltranslation.translator import translator, TranslationOptions
from .models import MyModel

class MyModelTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

translator.register(MyModel, MyModelTranslationOptions)
```

### How to use search vector field

#### SearchView

```python

from django.db.models import Q
from django.utils.translation import get_language
from django.views.generic import ListView

class SearchView(ListView):
    template_name = 'search/search_objects.html'
    paginate_by = 10
    multi_language = False # set True if you use multilingual search_vector field
    with_tags = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'search': self.request.GET.get('search', None) or ''})
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get('search', None)
        if query:
            if self.multi_language:
                current_language = get_language()
                return qs.filter(
                    Q(**{'search_vector_{}'.format(current_language): query}) |
                    Q(search_vector=query)
                )
            return qs.filter(search_vector=query)
        return qs
```

### urls.py

```python
from django.urls import path
from .views import SearchView
from .models import MyModel


app_name = 'search'
urlpatterns = [
    path('mymodels/', views.SearchView.as_view(queryset=MyModel.objects.all(), multi_language=True), name='mymodels'),
]

```

## Conclusion

This app is a solution, which is used by projects, developed by [Evgenii Legotckoi](https://www.linkedin.com/in/mr-evileg/)

This solution is provided for community "AS IS" without a warranty and can be used for any purpose under MIT License.