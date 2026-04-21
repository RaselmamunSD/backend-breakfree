from django.db import migrations


TIER_DATA = {
    "quiet-peaks": {
        "frequency_badge": "RARE",
        "name": "Quiet Peaks",
        "icon_key": "sun",
    },
    "passing-clouds": {
        "frequency_badge": "OCCASIONAL",
        "name": "Passing Clouds",
        "icon_key": "cloud",
    },
    "floating-clouds": {
        "frequency_badge": "FREQUENT",
        "name": "Floating Clouds",
        "icon_key": "rain",
    },
    "deep-swells": {
        "frequency_badge": "FREQUENT",
        "name": "Deep Swells",
        "icon_key": "storm",
    },
    "constant-flow": {
        "frequency_badge": "CONSTANT",
        "name": "Constant Flow",
        "icon_key": "wave",
    },
}

PROGRAM_DATA = {
    "foundation": {
        "journey_badge": "14 DAYS OF GENTLE GROWTH",
        "name": "The Foundation",
        "description": "Daily micro-shifts.",
    },
    "transformation": {
        "journey_badge": "30 DAYS OF DEEP RESILIENCE",
        "name": "The Transformation",
        "description": "Habit-building and emotional safety.",
    },
}


def apply_figma_copy(apps, schema_editor):
    SubscriptionTier = apps.get_model("onboarding", "SubscriptionTier")
    JourneyProgram = apps.get_model("onboarding", "JourneyProgram")
    for slug, fields in TIER_DATA.items():
        SubscriptionTier.objects.filter(slug=slug).update(**fields)
    for slug, fields in PROGRAM_DATA.items():
        JourneyProgram.objects.filter(slug=slug).update(**fields)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("onboarding", "0003_journeyprogram_journey_badge_and_more"),
    ]

    operations = [
        migrations.RunPython(apply_figma_copy, noop_reverse),
    ]
