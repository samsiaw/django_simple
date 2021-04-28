from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
# from django.contrib.postgres.fields import ArrayField

# REVIEW: You don't need all the models in the admin page

class User(AbstractUser):
    # username, email, password,
    username = models.CharField(unique=True, blank=False, max_length=64)

    def __str__(self):
        return f"{self.username}"


class Bid(models.Model):
    highest_bidder = models.ForeignKey(User, blank=True, on_delete=models.CASCADE,
                                       null=True)
    current_price = models.IntegerField(blank=False)

    def __str__(self):
        return f"Bid: ${self.current_price}"
# bids_model
#   starting bid
#   current price
# No need to link a bid to its listing.
# But link an listing to its bid


class Listing(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name="created_listing")
    # REVIEW: on_delete is on PROTECT
    winner = models.ForeignKey(User, on_delete=models.PROTECT,
                               related_name="won_listing", blank=True,
                               null=True)
    title = models.CharField(max_length=64, unique=True,)
    description = models.TextField(blank=True, )

    image = models.URLField(blank=True, null=True)
    active = models.BooleanField(default=True)

    # WARNING: Deleting bid would delete Listing. Check
    bid = models.OneToOneField(Bid, on_delete=models.CASCADE, related_name="listing")
    # comments = models.JSONField(default='{c_list:[]}')

    def get_shortDescr(self):
        d= f"{self.description}"[0:75]
        return d

    def __str__(self):
        if self.active:
            return f"{self.title} - active"
        return f"{self.title} - inactive"

# listing_model
# listing contains:
#   title
#   image
#   text based description
#   category / tag for Listings {create a model}
#   comments on current listing: many-to-one
#   bid on listing
#   active / not active detection
#   user (winner of inactive listing)
#   user (creator)

class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="watchlist")
    list = models.ManyToManyField(Listing, related_name="watched_by")

    def __str__(self):
        return f"{self.user.username}'s Watchlist: {self.list}"

    def get_active_listings(self):
        return self.list.all().filter(active=True)

    def get_inactive_listings(self):
        return self.list.all().filter(active=False)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="comments")
    user_comment = models.TextField(blank=False, )
    listing = models.ForeignKey(Listing,
                                related_name="comments",
                                on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user} -> {self.user_comment}"
# comments_model on auctions
#   user who passed comment:
#   comment of the user:

class Category(models.Model):
    name = models.CharField(max_length=64, blank=False, unique=True)

    connection = models.ManyToManyField(Listing, related_name="categories")

    def __str__(self):
        return self.name
