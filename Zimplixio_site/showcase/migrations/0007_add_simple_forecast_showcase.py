from django.db import migrations


def create_simple_forecast_showcase(apps, schema_editor):
    TechTag = apps.get_model('showcase', 'TechTag')
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')

    tag_names = ['Python', 'Django', 'React', 'PostgreSQL', 'Recharts', 'Anthropic Claude', 'Railway']
    tags = []
    for name in tag_names:
        tag, _ = TechTag.objects.get_or_create(name=name)
        tags.append(tag)

    project = ShowcaseProject.objects.create(
        title='Simple Forecast',
        slug='simple-forecast',
        summary=(
            'A Lean Six Sigma sales forecasting platform that transforms Excel data into a full '
            'LSS analytics report — SPC charts, process capability, 24-month forecasts, and safety '
            'stock calculations — delivered through plain-language dashboards for sales managers '
            'and operations leads.'
        ),
        business_problem=(
            'Sales managers and operations leads make monthly inventory and demand decisions, but '
            'traditional Lean Six Sigma analytics tools are built for Black Belts — not business '
            'users. Teams were relying on raw Excel files, computing forecasts manually, and making '
            'supply decisions without SPC control limits, capability indices, or safety stock '
            'guidance. The expertise gap meant that powerful statistical tools sat unused while '
            'decisions were made on gut feel.'
        ),
        approach=(
            'Design a single-server web application that abstracts the full LSS analytics pipeline '
            'behind a simple drag-and-drop Excel upload. Run all computations server-side across '
            'twelve pure-function services, then surface results through interactive charts with '
            'plain-language explanations written for non-technical users. Pair the analytics engine '
            'with a Claude AI assistant that acts as an on-demand Black Belt analyst — letting users '
            'ask questions about their own data without needing LSS expertise.'
        ),
        solution_description=(
            'Simple Forecast ingests Excel files with sales, demand, and supply records, '
            'auto-detects the data format, and runs a twelve-service analytics pipeline covering '
            'SPC X-bar R charts with Western Electric Rules, Cp/Cpk and Pp/Ppk process capability, '
            'safety stock at 95% and 99% service levels, 24-month combined forecasts using trend, '
            'seasonality, and exponential smoothing, demand/supply gap analysis, run charts, scatter '
            'plots, and normal probability plots. Results are organized across two chart tabs — '
            'Core Analysis and Deep Dive — with animated KPI chips, info modals written for '
            'non-technical users, per-product parameter tuning, and a streaming AI chat panel '
            'powered by Claude.'
        ),
        outcomes=(
            'Sales managers and operations leads can upload their monthly Excel file and receive '
            'a full LSS analytics report in seconds — no statistics background required. The '
            'platform handles multi-product portfolios with persistent parameter state, runs on '
            'Railway with a PostgreSQL backend, and serves interactive chart dashboards through a '
            'dark-themed React frontend. The AI chat assistant bridges the expertise gap, letting '
            'business users ask follow-up questions and act on insights without a Black Belt on '
            'the team.'
        ),
        live_demo_url='https://simple-forecast.com/',
        industry='cross-industry',
        is_published=True,
        order=2,
    )
    project.tech_tags.set(tags)


def remove_simple_forecast(apps, schema_editor):
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')
    ShowcaseProject.objects.filter(slug='simple-forecast').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('showcase', '0006_add_react_vite_tags_to_framework'),
    ]

    operations = [
        migrations.RunPython(create_simple_forecast_showcase, remove_simple_forecast),
    ]
