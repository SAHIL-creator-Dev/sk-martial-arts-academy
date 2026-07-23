from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import (
    ClassProgram,
    Instructor,
    Tournament,
    ClassUpdate,
    GalleryCategory,
    GalleryImage,
    ContactMessage,
    SiteSettings,
    AcademyStatistic,
)
from .utils import validate_image_file


# Admin forms with server-side upload validation (MIME, size, and integrity)
class InstructorAdminForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = "__all__"

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            validate_image_file(photo, allowed_mime_types=['image/jpeg', 'image/png'], max_bytes=getattr(settings, 'DEFAULT_MAX_UPLOAD_SIZE', 5 * 1024 * 1024))
        return photo


class TournamentAdminForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = "__all__"

    def clean_poster(self):
        poster = self.cleaned_data.get('poster')
        if poster:
            validate_image_file(poster, allowed_mime_types=['image/jpeg', 'image/png'], max_bytes=getattr(settings, 'DEFAULT_MAX_UPLOAD_SIZE', 5 * 1024 * 1024))
        return poster


class GalleryImageAdminForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = "__all__"

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            validate_image_file(image, allowed_mime_types=['image/jpeg', 'image/png'], max_bytes=getattr(settings, 'DEFAULT_MAX_UPLOAD_SIZE', 5 * 1024 * 1024))
        return image



@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("hero_tagline", "hero_video_url")

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ClassProgram)
class ClassProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "age_group", "schedule", "order")


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    form = InstructorAdminForm
    list_display = ("name", "title", "belt_rank", "order")


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    form = TournamentAdminForm
    list_display = ("title", "date", "location", "is_featured")
    list_filter = ("is_featured",)


@admin.register(ClassUpdate)
class ClassUpdateAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "is_featured")
    list_filter = ("is_featured",)


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")
    search_fields = ("name",)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    form = GalleryImageAdminForm
    list_display = ("title", "category", "date", "order")
    list_filter = ("category",)
    autocomplete_fields = ("category",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "submitted_at")


@admin.register(AcademyStatistic)
class AcademyStatisticAdmin(admin.ModelAdmin):
    list_display = ("value", "title", "display_order", "is_active")
    ordering = ("display_order",)
    search_fields = ("title",)
    list_filter = ("is_active",)
