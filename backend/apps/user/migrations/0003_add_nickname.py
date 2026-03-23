# Migration to add nickname field and update username verbose_name

from django.db import migrations, models


def populate_nickname_from_username(apps, schema_editor):
    """为已有用户设置昵称为其用户ID"""
    User = apps.get_model('user', 'User')
    User.objects.filter(nickname='').update(nickname=models.F('username'))


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='nickname',
            field=models.CharField(default='', max_length=20, verbose_name='用户昵称'),
        ),
        migrations.RunPython(
            populate_nickname_from_username,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=20, unique=True, verbose_name='用户ID'),
        ),
    ]
