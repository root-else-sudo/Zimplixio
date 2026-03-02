from django.db import models


class TechTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ShowcaseProject(models.Model):
    INDUSTRY_CHOICES = [
        ('automotive', 'Automotive'),
        ('healthcare', 'Healthcare'),
        ('ecommerce', 'E-Commerce'),
        ('cross-industry', 'Cross-Industry'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    summary = models.TextField(help_text="Short summary for gallery cards.")
    business_problem = models.TextField(help_text="The Scenario — what challenge did the client face?")
    approach = models.TextField(help_text="The Approach — how did we tackle it?")
    solution_description = models.TextField(help_text="The Solution — what was built/delivered?")
    architecture_diagram = models.ImageField(upload_to='showcase/diagrams/', blank=True)
    outcomes = models.TextField(help_text="The Outcome — measurable results.")
    demo_url = models.URLField(blank=True)
    live_demo_url = models.URLField(blank=True, help_text="URL to embed in an interactive iframe demo.")
    system_design_url = models.URLField(blank=True, help_text="URL for the system-design view toggle.")
    thumbnail = models.ImageField(upload_to='showcase/thumbnails/', blank=True)
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, default='cross-industry')
    tech_tags = models.ManyToManyField(TechTag, blank=True, related_name='projects')
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class ShowcaseScreenshot(models.Model):
    project = models.ForeignKey(ShowcaseProject, on_delete=models.CASCADE, related_name='screenshots')
    image = models.ImageField(upload_to='showcase/screenshots/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.title} — Screenshot {self.order}"
