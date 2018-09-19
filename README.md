
## Data Uploader

Upload csv files in django admin site, and batch create objects for the specified models.


### DataInputField

It provides a DataInputField django model field which can be used as:

```python
class LoadData(models.Model):
    for_model_1 = DataInputField(app_label='xxx', model_name='model1', order=1)
    for_model_2 = DataInputField(app_label='xxx', model_name='model2', order=2, load_func=_custom_load_func)
```

The order is the order by which the csv files are processed.

The load_func is a function which takes two arguments(model: models.Model and line: OrderedDict).
If not provided, will use a default load function:

```python
model.objects.create(**line)
```


### Action

A load_csv_files admin action which gets all csv files for the selected records and create objects for the specified model.
