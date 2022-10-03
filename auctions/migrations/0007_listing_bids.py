# Generated by Django 4.1.1 on 2022-10-03 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_bid_listing'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='bids',
            field=models.ManyToManyField(blank=True, null=True, related_name='listingBids', to='auctions.bid'),
        ),
    ]
