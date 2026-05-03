from django.db import migrations


def seed(apps, schema_editor):
    PremiumPlan = apps.get_model("features", "PremiumPlan")
    if PremiumPlan.objects.exists():
        return
    PremiumPlan.objects.create(
        name="Monthly",
        plan_key="monthly-default",
        price="9.99",
        billing_cycle="monthly",
        badge_tag="REGULAR",
        sort_order=0,
        ui_version="new",
        is_legacy=False,
        is_active=True,
        feature_summary="Seeded for local / Postman testing.",
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("features", "0003_seed_default_content"),
    ]

    operations = [migrations.RunPython(seed, noop)]
