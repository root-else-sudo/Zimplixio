from django.db import migrations


def clear_demo_url(apps, schema_editor):
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')
    ShowcaseProject.objects.filter(slug='ai-adoption-framework').update(demo_url='')


def restore_demo_url(apps, schema_editor):
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')
    ShowcaseProject.objects.filter(slug='ai-adoption-framework').update(demo_url='/framework/')


class Migration(migrations.Migration):

    dependencies = [
        ('showcase', '0003_ai_framework_showcase_entry'),
    ]

    operations = [
        migrations.RunPython(clear_demo_url, restore_demo_url),
    ]
