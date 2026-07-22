from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import (
    ClassProgram,
    Instructor,
    Tournament,
    ClassUpdate,
    GalleryCategory,
    GalleryImage,
    SiteSettings,
)
from .forms import ContactForm
from .utils import youtube_embed_url


def home(request):
    settings_obj = SiteSettings.load()
    programs = ClassProgram.objects.all()[:3]
    instructors = Instructor.objects.all()[:3]
    today = timezone.localdate()
    featured_tournaments = Tournament.objects.filter(is_featured=True, date__gte=today)[:2]
    featured_updates = ClassUpdate.objects.filter(is_featured=True)[:3]
    return render(request, "core/home.html", {
        "programs": programs,
        "instructors": instructors,
        "hero_embed_url": youtube_embed_url(settings_obj.hero_video_url),
        "hero_tagline": settings_obj.hero_tagline,
        "featured_tournaments": featured_tournaments,
        "featured_updates": featured_updates,
    })


def about(request):
    instructors = Instructor.objects.all()
    return render(request, "core/about.html", {"instructors": instructors})


def classes(request):
    programs = ClassProgram.objects.all()
    return render(request, "core/classes.html", {"programs": programs})


def gallery(request):
    categories = GalleryCategory.objects.all()
    featured_images = GalleryImage.objects.all()[:8]
    return render(request, "core/gallery.html", {
        "categories": categories,
        "featured_images": featured_images,
    })


def gallery_category(request, slug):
    category = get_object_or_404(GalleryCategory, slug=slug)
    categories = GalleryCategory.objects.all()
    images = category.images.all()
    return render(request, "core/gallery_category.html", {
        "category": category,
        "categories": categories,
        "images": images,
    })


def updates(request):
    today = timezone.localdate()
    upcoming_tournaments = Tournament.objects.filter(date__gte=today)
    past_tournaments = Tournament.objects.filter(date__lt=today)
    class_updates = ClassUpdate.objects.all()
    return render(request, "core/updates.html", {
        "upcoming_tournaments": upcoming_tournaments,
        "past_tournaments": past_tournaments,
        "class_updates": class_updates,
    })


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Message sent. We'll get back to you soon.")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})
