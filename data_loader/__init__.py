import csv

from django.apps import apps
from django.contrib import messages
from django.db import connections, models
from django.db.models.fields.files import FileField
from django.utils.translation import gettext_lazy as _


class DataInputField(FileField):
    description = _("upload csv files in admin site to insert data")

    def __init__(self, app_label, model_name, order, load_func=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_label = app_label
        self.model_name = model_name
        self.order = order
        self.load_func = load_func

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['app_label'] = self.app_label
        kwargs['model_name'] = self.model_name
        kwargs['order'] = self.order
        if self.load_func is not None:
            kwargs['load_func'] = self.load_func
        return name, path, args, kwargs


def load_csv_files(modeladmin, request, queryset):
    try:
        for obj in queryset:
            loot_fields = [f for f in obj._meta.fields if isinstance(f, DataInputField)]
            ordered_fields = sorted(loot_fields, key=lambda x: x.order)

            for field in ordered_fields:
                model = _get_model(field.app_label, field.model_name)
                # if want to remove all existing records, uncomment the following line
                # _truncate_table(model)
                _validate_csv_format(obj, field)

                file = getattr(obj, field.name)
                with open(file.path, 'r') as f:
                    reader = csv.DictReader(f, delimiter=',')

                    if field.load_func is None:
                        model.objects.bulk_create([model(**line) for line in reader])
                    else:
                        for line in reader:
                            field.load_func(model, line)
    except Exception as e:
        modeladmin.message_user(request, e, level=messages.ERROR)
    modeladmin.message_user(request, 'All data successfully inserted', level=messages.INFO)


def _truncate_table(model: models.Model):
    with connections['default'].cursor() as c:
        c.execute('SET FOREIGN_KEY_CHECKS = 0')
        c.execute(f'TRUNCATE {model._meta.db_table}')
        c.execute('SET FOREIGN_KEY_CHECKS = 1')


def _get_model(app_label: str, model_name: str) -> models.Model:
    try:
        return apps.get_model(app_label=app_label, model_name=model_name)
    except Exception:
        raise Exception('model-not-found')


def _validate_csv_format(obj, field: DataInputField):
    file = getattr(obj, field.name)
    if '.csv' not in file.name:
        raise Exception('invalid-file-type')
