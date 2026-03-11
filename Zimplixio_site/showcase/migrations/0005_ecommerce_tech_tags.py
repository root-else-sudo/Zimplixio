from django.db import migrations


def add_ecommerce_tags(apps, schema_editor):
    TechTag = apps.get_model('showcase', 'TechTag')
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')

    tag_names = [
        'Python', 'Django', 'PostgreSQL', 'Bootstrap 5',
        'jQuery', 'Railway', 'ONVO Pay', 'WhiteNoise',
    ]
    tags = []
    for name in tag_names:
        tag, _ = TechTag.objects.get_or_create(name=name)
        tags.append(tag)

    try:
        project = ShowcaseProject.objects.get(slug='e-commerce')
        project.tech_tags.set(tags)
    except ShowcaseProject.DoesNotExist:
        pass


def remove_ecommerce_tags(apps, schema_editor):
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')
    try:
        project = ShowcaseProject.objects.get(slug='e-commerce')
        project.tech_tags.clear()
    except ShowcaseProject.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('showcase', '0004_clear_framework_demo_url'),
    ]

    operations = [
        migrations.RunPython(add_ecommerce_tags, remove_ecommerce_tags),
    ]
