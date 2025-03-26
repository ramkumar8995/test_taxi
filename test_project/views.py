from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")  # Ensure this matches the form field
        password2 = request.POST.get("password2")  # Ensure this matches the form field

        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required!")
            return render(request, "register.html")

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return render(request, "register.html")

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect("login")

    return render(request, "register.html")


# Login User
def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Invalid credentials! Please try again.")
            return redirect("login")

    return render(request, "login.html")


from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect("login")

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum
from taxi_app.models import Trip

@login_required
def index(request):
    today = datetime.now().date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)
    this_year_start = today.replace(month=1, day=1)

    # If the user is a superuser, show all trips, otherwise filter by the logged-in user
    if request.user.is_superuser:
        trips = Trip.objects.all().order_by("-trip_time")
    else:
        trips = Trip.objects.filter(driver=request.user).order_by("-trip_time")

    # Calculate earnings based on the trips shown to the user
    daily_total = trips.filter(trip_time__date=today).aggregate(Sum('fare'))['fare__sum'] or 0
    weekly_total = trips.filter(trip_time__date__gte=this_week_start).aggregate(Sum('fare'))['fare__sum'] or 0
    monthly_total = trips.filter(trip_time__date__gte=this_month_start).aggregate(Sum('fare'))['fare__sum'] or 0
    yearly_total = trips.filter(trip_time__date__gte=this_year_start).aggregate(Sum('fare'))['fare__sum'] or 0

    if request.method == "POST":
        from_place = request.POST.get("from_place")
        to_place = request.POST.get("to_place")
        fare = request.POST.get("fare", "0")
        payment_type = request.POST.get("payment_type")
        tip = request.POST.get("tip", "0")

        try:
            fare = Decimal(fare)
        except:
            fare = Decimal("0.00")

        try:
            tip = Decimal(tip)
        except:
            tip = Decimal("0.00")

        if from_place and to_place and payment_type:
            Trip.objects.create(
                driver=request.user,  # Assign the logged-in user as the driver
                trip_time=datetime.now(),
                from_place=from_place,
                to_place=to_place,
                fare=fare,
                payment_type=payment_type,
                tip=tip
            )
            return redirect("index")

    return render(request, "index.html", {
        "trips": trips,
        "daily_total": daily_total,
        "weekly_total": weekly_total,
        "monthly_total": monthly_total,
        "yearly_total": yearly_total,
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from taxi_app.models import Trip

@login_required
def search_trips(request):
    query = request.GET.get("q", "")
    trips = Trip.objects.all()

    # Apply search filter (case-insensitive) for from_place, to_place, or driver.username
    if query:
        trips = trips.filter(
            Q(driver__username__icontains=query) |
            Q(from_place__icontains=query) |
            Q(to_place__icontains=query)
        )

    # If the user is not an admin, filter only their trips
    if not request.user.is_superuser:
        trips = trips.filter(driver=request.user)

    return render(request, "search_trips.html", {"trips": trips, "query": query})
