from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from .utils import sanitize_filename


BELT_CHOICES = [
    ("white", "White Belt"),
    ("yellow", "Yellow Belt"),
    ("orange", "Orange Belt"),
    ("green", "Green Belt"),
    ("blue", "Blue Belt"),
    ("purple", "Purple Belt"),
    ("brown", "Brown Belt"),
    ("black", "Black Belt"),
]


class ClassProgram(models.Model):
    """A training program / batch, e.g. Kids Karate, Self-Defense."""
    name = models.CharField(max_length=100)
    age_group = models.CharField(max_length=60, blank=True)
    schedule = models.CharField(max_length=120, help_text="e.g. Mon/Wed/Fri, 5:00-6:00 PM")
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Instructor(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True, help_text="e.g. Sempai, Sensei, North India Chief")
    belt_rank = models.CharField(max_length=20, choices=BELT_CHOICES, default="black")
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="instructors/", blank=True, null=True, validators=[FileExtensionValidator(["jpg","jpeg","png"])])
    order = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Lightweight filename sanitization to prevent path traversal and unsafe names.
        try:
            if getattr(self, 'photo', None) and hasattr(self.photo, 'name') and self.photo.name:
                cleaned = sanitize_filename(self.photo.name)
                if not cleaned:
                    raise ValidationError('Invalid filename for instructor photo.')
                self.photo.name = cleaned
        except ValidationError:
            raise
        except Exception:
            # Do not block save on unexpected sanitizer errors; admin can re-upload if needed.
            pass

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class Tournament(models.Model):
    """An upcoming or past tournament / competition."""
    title = models.CharField(max_length=150)
    date = models.DateField()
    location = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    poster = models.ImageField(upload_to="tournaments/", blank=True, null=True, validators=[FileExtensionValidator(["jpg","jpeg","png"])])
    is_featured = models.BooleanField(default=False, help_text="Show on the home page")

    def save(self, *args, **kwargs):
        # Lightweight filename sanitization for poster
        try:
            if getattr(self, 'poster', None) and hasattr(self.poster, 'name') and self.poster.name:
                cleaned = sanitize_filename(self.poster.name)
                if not cleaned:
                    raise ValidationError('Invalid filename for tournament poster.')
                self.poster.name = cleaned
        except ValidationError:
            raise
        except Exception:
            pass

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.title} ({self.date:%d %b %Y})"


class ClassUpdate(models.Model):
    """A short news/update item about classes, timings, grading, closures, etc."""
    title = models.CharField(max_length=150)
    date = models.DateField()
    body = models.TextField()
    is_featured = models.BooleanField(default=False, help_text="Show on the home page")

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} ({self.date:%d %b %Y})"


class GalleryCategory(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Gallery Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class GalleryImage(models.Model):
    category = models.ForeignKey(
        GalleryCategory,
        related_name="images",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=150, blank=True)
    caption = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="gallery/%Y/%m/%d", validators=[FileExtensionValidator(["jpg","jpeg","png"])])
    order = models.PositiveIntegerField(default=0)
    date = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Lightweight filename sanitization for gallery image
        try:
            if getattr(self, 'image', None) and hasattr(self.image, 'name') and self.image.name:
                cleaned = sanitize_filename(self.image.name)
                if not cleaned:
                    raise ValidationError('Invalid filename for gallery image.')
                self.image.name = cleaned
        except ValidationError:
            raise
        except Exception:
            pass

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or self.caption or f"Image {self.pk}"


class SiteSettings(models.Model):
    """Singleton — editable from the admin so the academy can swap the hero video without touching code."""
    hero_video_url = models.URLField(
        blank=True,
        help_text="YouTube watch or embed URL, e.g. https://www.youtube.com/watch?v=XXXXXXXXXXX",
    )
    hero_tagline = models.CharField(max_length=200, blank=True, default="Discipline is the first kata.")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.name} - {self.submitted_at:%d %b %Y}"
