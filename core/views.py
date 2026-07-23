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
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import logging


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
            # Persist the submission (existing behavior)
            submission = form.save()

            # Prepare email context and content
            context = {
                "name": form.cleaned_data.get("name"),
                "email": form.cleaned_data.get("email"),
                "phone": form.cleaned_data.get("phone"),
                "message": form.cleaned_data.get("message"),
                "datetime": timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S %Z"),
            }

            subject = f"Website Contact: {context['name']}"
            html_message = render_to_string("emails/contact_email.html", context)

            # Send to the configured email receiver (use EMAIL_HOST_USER as the recipient if present)
            to_email = [getattr(settings, "EMAIL_HOST_USER", None)] if getattr(settings, "EMAIL_HOST_USER", None) else [getattr(settings, "DEFAULT_FROM_EMAIL", None)]
            # Fallback ensure list of non-empty targets
            to_email = [e for e in to_email if e]

            try:
                if to_email:
                    email_message = EmailMessage(
                        subject=subject,
                        body=html_message,
                        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "EMAIL_HOST_USER", None),
                        to=to_email,
                    )
                    email_message.content_subtype = "html"
                    email_message.send(fail_silently=False)
                else:
                    logging.warning("No recipient configured for contact emails; skipping send.")
            except Exception:
                # Log for internal debugging but don't expose exceptions to site visitors
                logging.exception("Failed to send contact form email")
                # Show a user-friendly error message and preserve the form data/validation
                messages.error(request, "❌ Sorry, we couldn't send your message at the moment. Please try again later.")
                return render(request, "core/contact.html", {"form": form})

            # On successful send, use PRG and a friendly success message
            messages.success(request, "✅ Thank you! Your message has been sent successfully. We will contact you soon.")
            return redirect("contact")
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {"form": form})
