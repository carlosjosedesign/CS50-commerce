from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listing, Bid, Comment


def index(request):
    activeListings = Listing.objects.filter(isActive=True)
    Categories = Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings": activeListings,
        'categories': Categories
    })

def displayCategory(request):
    if request.method == "POST":
        categoryFrom = request.POST["category"]

        if categoryFrom == 'all':
            return HttpResponseRedirect( reverse(index) )

        category = Category.objects.get(id=categoryFrom)
        activeListings = Listing.objects.filter(isActive=True, category=category)
        Categories = Category.objects.all()
        return render(request, "auctions/index.html",{
            "listings": activeListings,
            'categories': Categories,
            "nowCategory": float(categoryFrom),
        })

def listing(request, id):
    listingData = Listing.objects.get(pk=id)
    isListingWatchList = request.user in listingData.watchlist.all()
    allComments = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username == listingData.owner.username
    
    if 'message' in request.GET:
        message = request.GET['message']
        if 'status' in request.GET:
            status = request.GET['status']
    else:
        message = False
        status = False

    return render(request, "auctions/listing.html",{
        'listing': listingData,
        'isListingWatchList':isListingWatchList, 
        'allComments':allComments,
        'isOwner':isOwner,
        'message':message,
        'status':status
    })

def displayWatchList(request):
    currentUser = request.user
    listings =currentUser.listingWatchList.all()
    return render(request, "auctions/watchlist.html",{
        'listings': listings,
    })

def removeWatchList(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect( reverse("listing", args=(id, ) ))

def addWatchList(request, id):
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect( reverse("listing", args=(id, ) ))

def addBid(request, id):
    newVBid = request.POST['newBid']
    listingData = Listing.objects.get(pk=id)
    nowBid = 0
    if listingData.price and listingData.price.bid:
        nowBid = listingData.price.bid
        
    if int(newVBid) > nowBid:
        updateBid = Bid(user=request.user, bid=int(newVBid), listing=listingData )
        updateBid.save()
        listingData.bids.add(updateBid)
        listingData.price = updateBid
        listingData.save()
        return HttpResponseRedirect( reverse('listing', kwargs={'id': id})+'?message=Bid was updated successfuly&status=success' )
    else:
        return HttpResponseRedirect( reverse('listing', kwargs={'id': id})+'?message=Bid updated failed&status=error' )
    
def closeAuction(request, id):
    listingData = Listing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    return HttpResponseRedirect( reverse('listing', kwargs={'id': id})+'?message=Congratulations! Your auction is closed.&status=success' )

def addComment(request, id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST['message']

    newComment = Comment(
        author=currentUser,
        listing=listingData,
        message=message
    )
    newComment.save()

    return HttpResponseRedirect( reverse("listing", args=(id, ) ))

def myAuctions(request):
    currentUser = request.user
    bids = currentUser.userBid.all()
    listings = Listing.objects.filter(bids__in=bids).distinct()
    ownAuctions = Listing.objects.filter(owner=currentUser)

    return render(request, "auctions/myauctions.html",{
        "listings": listings,
        "ownAuctions":ownAuctions,
    })

def createListing(request):
    if request.method == 'GET':
        Categories = Category.objects.all();
        return render(request, "auctions/create.html", 
            {'categories': Categories}
        )
    else:
        title = request.POST["title"]
        description = request.POST["description"]
        imageUrl = request.POST["imageUrl"]
        price = request.POST["price"]
        category = Category.objects.get(id=request.POST["category"])
        currentUser = request.user

        bid = Bid(bid=int(price), user=currentUser)
        bid.save()

        newListing = Listing(
            title=title,
            description=description,
            imageUrl=imageUrl,
            price=bid,
            category=category,
            owner=currentUser
        )

        newListing.save()

        bid.listing = newListing
        bid.save()

        return HttpResponseRedirect( reverse(index) )

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
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
