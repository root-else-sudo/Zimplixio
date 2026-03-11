from django.db import migrations


def create_framework_showcase(apps, schema_editor):
    TechTag = apps.get_model('showcase', 'TechTag')
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')

    # Create or get tech tags
    tag_names = ['Python', 'Django', 'Anthropic Claude', 'Prompt Engineering', 'Tailwind CSS', 'Vanilla JS']
    tags = []
    for name in tag_names:
        tag, _ = TechTag.objects.get_or_create(name=name)
        tags.append(tag)

    # Create the showcase project
    project = ShowcaseProject.objects.create(
        title='AI Adoption Framework',
        slug='ai-adoption-framework',
        summary=(
            'An interactive 6-stage AI adoption methodology for SMBs, paired with '
            'a personalized AI readiness assessment powered by Claude. Demonstrates '
            'prompt engineering, structured output parsing, and AI product design.'
        ),
        business_problem=(
            'Small and mid-sized businesses approach AI adoption as a tooling decision — '
            'which platform to buy, which model to use. This framing leads to underperformance '
            'because the real challenge is organizational: aligning people, processes, and '
            'governance around a new way of working. There was no practitioner-level framework '
            'designed specifically for SMBs.'
        ),
        approach=(
            'Built a structured 6-stage framework from real implementation experience across '
            'enterprise and SMB environments. Each stage addresses a specific organizational '
            'challenge — from readiness assessment through measurement and ROI. The framework '
            'is paired with an AI-powered assessment tool that provides personalized, actionable '
            'guidance based on the company\'s specific profile.'
        ),
        solution_description=(
            'A Django-based interactive page with two sections: (1) An accordion-style framework '
            'navigator presenting all 6 stages with real-world examples, comparison tables, and '
            'practitioner insights. (2) An 8-question guided assessment form that calls the '
            'Anthropic API server-side with a carefully engineered system prompt, returning '
            'structured JSON that renders as a personalized readiness report with readiness level, '
            'priority stage, risk analysis, 30-day action plan, and verdict.'
        ),
        outcomes=(
            'Demonstrates three key capabilities: (1) AI product design — the assessment delivers '
            'genuinely useful, profile-specific advice rather than generic recommendations. '
            '(2) Prompt engineering — the system prompt encodes the full framework methodology and '
            'enforces structured JSON output. (3) Full-stack implementation — Django backend with '
            'rate limiting, vanilla JS frontend with form wizard UX, and cohesive design system integration.'
        ),
        demo_url='/framework/',
        industry='cross-industry',
        is_published=True,
        order=0,
    )
    project.tech_tags.set(tags)


def remove_framework_showcase(apps, schema_editor):
    ShowcaseProject = apps.get_model('showcase', 'ShowcaseProject')
    ShowcaseProject.objects.filter(slug='ai-adoption-framework').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('showcase', '0002_showcaseproject_live_demo_url_and_more'),
    ]

    operations = [
        migrations.RunPython(create_framework_showcase, remove_framework_showcase),
    ]
