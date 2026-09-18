from django.contrib import admin
from django.forms.models import BaseModelFormSet


class AllObjectsAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        return self.model.all_objects.all()

    def get_changelist_formset(self, request, **kwargs):
        model_cls = self.model

        class ChangeListFormSet(BaseModelFormSet):
            def add_fields(self, form, index):
                super().add_fields(form, index)
                pk_name = model_cls._meta.pk.name
                if pk_name in form.fields:
                    form.fields[pk_name].queryset = model_cls.all_objects.all()

        kwargs["formset"] = ChangeListFormSet
        return super().get_changelist_formset(request, **kwargs)