# Generated by Django 4.2 on 2023-05-16 15:39

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("articles", "0001_initial"),
        ("misc", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="related_licenses",
            field=models.ManyToManyField(
                blank=True, related_name="related_articles", to="misc.license"
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="related_materials",
            field=models.ManyToManyField(
                blank=True, related_name="related_articles", to="misc.relatedmaterial"
            ),
        ),
        migrations.AddIndex(
            model_name="articleidentifier",
            index=models.Index(
                fields=["article_id", "identifier_type", "identifier_value"],
                name="articles_ar_article_e663d1_idx",
            ),
        ),
    ]