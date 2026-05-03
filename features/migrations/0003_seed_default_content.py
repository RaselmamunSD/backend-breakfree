# Generated manually — seed catalog rows for mobile clients.

from django.db import migrations


def seed(apps, schema_editor):
    BreathingExercise = apps.get_model("wellness", "BreathingExercise")
    WorryForecastTemplate = apps.get_model("features", "WorryForecastTemplate")
    CBTTip = apps.get_model("features", "CBTTip")
    AppContent = apps.get_model("features", "AppContent")
    ProgramTrack = apps.get_model("features", "ProgramTrack")
    ProgramDay = apps.get_model("features", "ProgramDay")

    if not BreathingExercise.objects.exists():
        BreathingExercise.objects.create(
            slug="box",
            name="Box Breathing",
            description="Inhale 4s, Hold 4s, Exhale 4s, Hold 4s",
            duration_minutes=4,
            total_cycles=15,
            difficulty_tag="BEGINNER",
            intensity_level=1,
            theme_color="teal",
            phases=[
                {"phase": "inhale", "seconds": 4},
                {"phase": "hold", "seconds": 4},
                {"phase": "exhale", "seconds": 4},
                {"phase": "hold", "seconds": 4},
            ],
        )
        BreathingExercise.objects.create(
            slug="four-seven-eight",
            name="4-7-8 Breathing",
            description="Inhale 4s, Hold 7s, Exhale 8s",
            duration_minutes=8,
            total_cycles=8,
            difficulty_tag="ADVANCED",
            intensity_level=2,
            theme_color="teal",
            phases=[
                {"phase": "inhale", "seconds": 4},
                {"phase": "hold", "seconds": 7},
                {"phase": "exhale", "seconds": 8},
            ],
        )
        BreathingExercise.objects.create(
            slug="slow",
            name="Slow Breathing",
            description="Inhale 4s, Exhale 6s",
            duration_minutes=2,
            total_cycles=10,
            difficulty_tag="RELAXATION",
            intensity_level=1,
            theme_color="pink",
            phases=[
                {"phase": "inhale", "seconds": 4},
                {"phase": "exhale", "seconds": 6},
            ],
        )

    templates = [
        ("embarrass", "I'll Embarrass Myself."),
        ("panic", "I'll Have A Panic Attack."),
        ("awkward", "They'll Think I'm Awkward."),
        ("cope", "Something Will Go Wrong And I Won't Cope."),
        ("mess_up", "I'll Mess It Up."),
    ]
    for i, (key, label) in enumerate(templates):
        WorryForecastTemplate.objects.get_or_create(
            key=key, defaults={"label": label, "sort_order": i, "is_active": True}
        )

    if not CBTTip.objects.exists():
        CBTTip.objects.create(
            body=(
                "Be specific. Instead of 'I'll feel bad,' try 'I will feel so dizzy that I have to sit down "
                "for 5 minutes.' This makes it easier to test later."
            ),
            sort_order=0,
            is_active=True,
        )

    AppContent.objects.get_or_create(
        key="emergency",
        defaults={
            "payload": {
                "disclaimer": "Educational wellness tools only — not a crisis service.",
                "us": {"call": "988", "text": "741741"},
                "message": "If you feel unsafe, contact local emergency services.",
            }
        },
    )
    AppContent.objects.get_or_create(
        key="social_links",
        defaults={
            "payload": {
                "tiktok": "https://www.tiktok.com/",
                "instagram": "https://www.instagram.com/",
            }
        },
    )
    AppContent.objects.get_or_create(
        key="premium_preview",
        defaults={
            "payload": {
                "headline": "Preview a Premium lesson",
                "quote": "Your nervous system can learn safety through repeated, gentle practice.",
            }
        },
    )
    AppContent.objects.get_or_create(
        key="feature_flags",
        defaults={"payload": {"premium_paywall_ui": "new", "onboarding_replay_enabled": True}},
    )

    program, _ = ProgramTrack.objects.get_or_create(
        slug="quick-start-14",
        defaults={
            "title": "14 Day Quick Start",
            "subtitle": "Start your journey today.",
            "total_days": 14,
            "free_preview_days": 3,
            "is_active": True,
            "sort_order": 0,
        },
    )
    if program.days.count() == 0:
        for n in range(1, 15):
            ProgramDay.objects.create(
                program=program,
                day_number=n,
                label_date="",
                title=f"Day {n} — Theme placeholder",
                short_description="Short summary for the journey list card.",
                content_body="Full lesson copy can be edited in Django admin.",
                action_steps=["Take one slow breath", "Name one fact you know is true right now"],
                journal_prompts=["What felt hardest today?", "What tiny win did you notice?"],
                regulation_tool={"title": "Regulation tool", "body": "Use box breathing for 60 seconds."},
            )


def unseed(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("features", "0002_appcontent_cbttip_guestquota_programtrack_and_more"),
        ("wellness", "0003_breathingexercise_breathingsession_cycles_completed_and_more"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
