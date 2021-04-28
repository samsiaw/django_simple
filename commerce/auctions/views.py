from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm

from .models import User, Listing, Bid, Category, Watchlist, Comment

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'image']

def index(request):
    context=dict()
    context["listings"] = Listing.objects.all().filter(active=True)
    return render(request, "auctions/index.html",context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            w = Watchlist(user = user)
            w.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def parseCategories(string):
    return string.split()

def create_listing(request):
    if request.method == "GET":
        return render(request, "auctions/new-listing.html", {"form":NewListingForm})

    else: # POST
        user = request.user
        user_id = user.id
        # Auction details
        title = request.POST.get('title','')
        bid = request.POST.get('bid','')
        img_link= request.POST.get('image_link','')
        category = request.POST.get('category','')
        description = request.POST.get("listing_descr",'')

        # Create Auction
        b1 = Bid(current_price=bid)
        b1.save()

        try:
            l1 = Listing(creator=user, title=title.capitalize(), description=description, bid=b1,
            image=img_link)
            l1.save()

        except IntegrityError:
            mess = f"Auction with title {title} already exists"
            context={"listings":Listing.objects.all().filter(active=True)}
            context["eMess"] = mess
            return render(request, "auctions/index.html", context)

        # Create categories from string
        for c in parseCategories(category):
            c= c.capitalize()
            if c!="All":
                try:
                    new_cat = Category(name=c)
                    new_cat.save()
                    new_cat.connection.add(l1)
                except IntegrityError:
                    #category exists
                    cat= Category.objects.get(name=c)
                    cat.connection.add(l1)
            else:
                context= dict()
                context["eMess"]="All not accepted as category name"

        mess = f"Auction: '{title}' created successfully"
        try:
            context == dict()
        except:
            context = dict()
        context["listings"] = Listing.objects.all().filter(active=True)
        context["sMess"] = mess
        return render(request, "auctions/index.html", context)

def listing(request, l_id):
    listing = Listing.objects.get(id=l_id)
    context = {"listing":listing}
    context['sMess'] = list()
    context['eMess'] = list()
    if request.method == "POST":
        user = request.user
        con = dict()
        #watchlist
        watch = request.POST.get('watchlist', '')
        if watch == 'T':
            user.watchlist.list.add(listing)
            context['sMess'].append("Added to watchlist")
        elif watch == 'F':
            user.watchlist.list.remove(listing)
            context['sMess'].append("Removed from watchlist")

        #Active/inactive
        active = request.POST.get('active', '')
        if active =='F':
            # Make highest_bidder the winner of the listing
            setattr(listing,'winner',listing.bid.highest_bidder)
            listing.save()
            setattr(listing,'active',False)
            listing.save()
            context['sMess'].append("Listing deactivated")

        #Bids
        bid = request.POST.get('new-bid', '')
        if bid:
            if int(bid)> listing.bid.current_price:
                setattr(listing.bid, 'highest_bidder',user)
                listing.bid.save()
                setattr(listing.bid,'current_price', int(bid) + 1)
                listing.bid.save()
                context['sMess'].append(f"Bid increased to {bid}")
            else:
                context['eMess'].append(f"Price lower than minimum bid price")
        #Commentary
        com = request.POST.get('comment','')
        if com.strip() != "":
            newCom = Comment(user=user, user_comment=com, listing=listing)
            newCom.save()
            context['sMess'].append("New Comment uploaded")

    return render(request, "auctions/info-page.html", context)

def watchlist(request):
    # TODO: User must be able to add or delete items from their Watchlist

    user = request.user
    w = user.watchlist
    context = {"watchlist": w}
    return render(request, "auctions/watchlist.html", context)

def categories(request, cat):
    # TODO: User must be able to select an existing category and view listings on it
    # TODO: First page should be all categories

    con = {"categories":Category.objects.all()}
    con["eMess"]=list()
    if cat.lower() == 'all':
        listing = Listing.objects.all()
        con["listings"] = listing

    else:
        if cat.strip() !='':
            try:
                category = Category.objects.get(name=cat.capitalize())
                listing= category.connection.all()
                con["listings"] = listing
            except:
                con["eMess"].append(f"Category: {cat.capitalize()} does not exist")
                return render(request, "auctions/categories.html",con )

        else:
            # Posted from category website
            category = request.POST.get('category','')
            if category.strip()!="":
                return categories(request, category)
            return categories(request, "All")

    return render(request, "auctions/categories.html",con )
