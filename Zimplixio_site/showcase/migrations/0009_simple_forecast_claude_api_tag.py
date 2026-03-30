from django.db import migrations


def swap_tag(apps, schema_editor):
    TechTag = apps.get_model('showcase', 'TechTag')
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')

    project = ShowcaseProject.objects.filter(slug='simple-forecast').first()
    if not project:
        return

    old_tag = TechTag.objects.filter(name='Anthropic Claude').first()
    if old_tag:
        project.tech_tags.remove(old_tag)

    new_tag, _ = TechTag.objects.get_or_create(name='Claude API')
    project.tech_tags.add(new_tag)


def revert_tag(apps, schema_editor):
    TechTag = apps.get_model('showcase', 'TechTag')
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')

    project = ShowcaseProject.objects.filter(slug='simple-forecast').first()
    if not project:
        return

    new_tag = TechTag.objects.filter(name='Claude API').first()
    if new_tag:
        project.tech_tags.remove(new_tag)

    old_tag, _ = TechTag.objects.get_or_create(name='Anthropic Claude')
    project.tech_tags.add(old_tag)


class Migration(migrations.Migration):

    dependencies = [
        ('showcase', '0008_simple_forecast_demo_url'),
    ]

    operations = [
        migrations.RunPython(swap_tag, revert_tag),
    ]
