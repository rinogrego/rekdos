# Generated by Django 4.0.2 on 2023-05-14 10:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rekomendasi', '0004_run_name_alter_peminatan_nama'),
    ]

    operations = [
        migrations.CreateModel(
            name='Run_Results',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(choices=[('Hu', 'Hungarian'), ('Kr', 'Kruskal')], max_length=2)),
                ('results', models.TextField(max_length=100000)),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='rekomendasi.run')),
            ],
        ),
    ]
