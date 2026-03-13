from django.db import migrations


def add_tags(apps, schema_editor):
    TechTag = apps.get_model('showcase', 'TechTag')
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')

    project = ShowcaseProject.objects.filter(slug='ai-adoption-framework').first()
    if not project:
        return

    for name in ['React', 'Vite']:
        tag, _ = TechTag.objects.get_or_create(name=name)
        project.tech_tags.add(tag)


def remove_tags(apps, schema_editor):
    TechTag = apps.get_model('showcase', 'TechTag')
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')

    project = ShowcaseProject.objects.filter(slug='ai-adoption-framework').first()
    if not project:
        return

    for name in ['React', 'Vite']:
        tag = TechTag.objects.filter(name=name).first()
        if tag:
            project.tech_tags.remove(tag)


class Migration(migrations.Migration):

    dependencies = [
        ('showcase', '0005_ecommerce_tech_tags'),
    ]

    operations = [
        migrations.RunPython(add_tags, remove_tags),
    ]
