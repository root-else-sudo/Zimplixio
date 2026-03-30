from django.db import migrations


def set_demo_url(apps, schema_editor):
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')
    ShowcaseProject.objects.filter(slug='simple-forecast').update(demo_url='https://simple-forecast.com/')


def clear_demo_url(apps, schema_editor):
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')
    ShowcaseProject.objects.filter(slug='simple-forecast').update(demo_url='')


class Migration(migrations.Migration):

    dependencies = [
        ('showcase', '0007_add_simple_forecast_showcase'),
    ]

    operations = [
        migrations.RunPython(set_demo_url, clear_demo_url),
    ]
