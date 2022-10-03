from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass
  
class Category(models.Model):
    categoryName = models.CharField(max_length=64)

    def __str__(self):
        return self.categoryName

class Bid(models.Model):
    bid = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userBid")
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, blank=True, null=True, related_name="listingBid")

    def __str__(self):
        return f"{self.bid} from {self.user}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=300)
    imageUrl = models.CharField(max_length=1000)
    price = models.ForeignKey(Bid, on_delete=models.SET_NULL, blank=True, null=True, related_name="bidPrice")
    bids = models.ManyToManyField(Bid, blank=True, null=True, related_name="listingBids")
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="listingWatchList")

    def __str__(self):
        return self.title

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userComment")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listingComment")
    message = models.CharField(max_length=500)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} comment on {self.listing} at {self.posted_at}"

