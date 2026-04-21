from django.db import migrations


def seed_catalog(apps, schema_editor):
    SubscriptionTier = apps.get_model("onboarding", "SubscriptionTier")
    JourneyProgram = apps.get_model("onboarding", "JourneyProgram")

    tiers = [
        ("quiet-peaks", "Quiet Peaks", "", 1),
        ("passing-clouds", "Passing Clouds", "", 2),
        ("floating-clouds", "Floating Clouds", "", 3),
        ("deep-swells", "Deep Swells", "", 4),
        ("constant-flow", "Constant Flow", "", 5),
    ]
    for slug, name, desc, order in tiers:
        SubscriptionTier.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "description": desc, "sort_order": order, "is_active": True},
        )

    programs = [
        (
            "foundation",
            "The Foundation",
            "Rebuild self-worth and confidence.",
            "",
            1,
        ),
        (
            "transformation",
            "The Transformation",
            "Dedicated to deep inner work.",
            "",
            2,
        ),
    ]
    for slug, name, desc, image, order in programs:
        JourneyProgram.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description": desc,
                "cover_image_url": image,
                "sort_order": order,
                "is_active": True,
            },
        )


def unseed_catalog(apps, schema_editor):
    SubscriptionTier = apps.get_model("onboarding", "SubscriptionTier")
    JourneyProgram = apps.get_model("onboarding", "JourneyProgram")
    SubscriptionTier.objects.filter(
        slug__in=[
            "quiet-peaks",
            "passing-clouds",
            "floating-clouds",
            "deep-swells",
            "constant-flow",
        ]
    ).delete()
    JourneyProgram.objects.filter(slug__in=["foundation", "transformation"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("onboarding", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_catalog, unseed_catalog),
    ]
