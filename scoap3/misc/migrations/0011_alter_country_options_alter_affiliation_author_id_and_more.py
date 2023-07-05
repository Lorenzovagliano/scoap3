# Generated by Django 4.2.2 on 2023-07-05 09:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authors", "0003_alter_author_first_name_alter_author_last_name"),
        ("articles", "0005_articlefile_rename_created_at_article__created_at_and_more"),
        ("misc", "0010_alter_affiliation_author_id_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="country",
            options={"ordering": ["code"], "verbose_name_plural": "Countries"},
        ),
        migrations.AlterField(
            model_name="affiliation",
            name="author_id",
            field=models.ManyToManyField(blank=True, to="authors.author"),
        ),
        migrations.AlterField(
            model_name="experimentalcollaboration",
            name="article_id",
            field=models.ManyToManyField(blank=True, to="articles.article"),
        ),
    ]
