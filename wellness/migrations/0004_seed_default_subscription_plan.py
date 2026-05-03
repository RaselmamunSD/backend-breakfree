from django.db import migrations


def seed(apps, schema_editor):
    SubscriptionPlan = apps.get_model("wellness", "SubscriptionPlan")
    if SubscriptionPlan.objects.exists():
        return
    SubscriptionPlan.objects.create(
        name="Default Monthly",
        plan_type="monthly",
        price="9.99",
        discount_label="REGULAR",
        is_active=True,
        description="Seeded for local / Postman testing.",
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("wellness", "0003_breathingexercise_breathingsession_cycles_completed_and_more"),
    ]

    operations = [migrations.RunPython(seed, noop)]
