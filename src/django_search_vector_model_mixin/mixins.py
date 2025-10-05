from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models

class SearchVectorModelMixin(models.Model):
    search_vector = SearchVectorField(null=True)
    search_fields = None

    class Meta:
        abstract = True
        indexes = [
            GinIndex(fields=["search_vector"]),
        ]

    def update_search_vector(self):
        if not self.search_fields or len(self.search_fields) == 0:
            raise ValueError("Define search_fields in your model")

        vectors = {'search_vector': SearchVector(*self.search_fields)}

        cls = type(self)
        qs = cls.objects.filter(pk=self.pk)
        qs.update(**vectors)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_search_vector()


def make_search_vector_mixin():
    class ModelMixin(SearchVectorModelMixin):

        class Meta(SearchVectorModelMixin.Meta):
            abstract = True
            indexes = [
                GinIndex(fields=["search_vector"] + [
                    f"search_vector_{code}" for code, _ in settings.LANGUAGES
                ]),
            ]

        def update_search_vector(self):
            if not self.search_fields or len(self.search_fields) == 0:
                raise ValueError("Define search_fields in your model")

            vectors = {'search_vector': SearchVector(*self.search_fields)}

            for code, language in settings.LANGUAGES:
                vectors[f'search_vector_{code}'] = SearchVector(*[f'{search_field}_{code}' for search_field in self.search_fields])

            cls = type(self)
            qs = cls.objects.filter(pk=self.pk)
            qs.update(**vectors)

    for code, _ in settings.LANGUAGES:
        field_name = f"search_vector_{code}"
        if not hasattr(ModelMixin, field_name):
            field = SearchVectorField(null=True)
            field.contribute_to_class(ModelMixin, field_name)

    return ModelMixin

MultilingualSearchVectorModelMixin = make_search_vector_mixin()
