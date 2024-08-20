from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.db import models
import requests
import uuid
import datetime
import pytz
from .utils import get_location_and_weather



def home(request):
    # Check if the user has entered their name
    if 'user_name' not in request.session:
        return redirect('name_input')  # Redirect if name is not in session

    # Fetch and sort visitors by the number of visitors in descending order
    visitors = Visitor.objects.exclude(country='Unknown').values('country').annotate(visitors=Count('id')).order_by('-visitors')
    visitor_count = Visitor.objects.exclude(country='Unknown').count()

    rating_id = request.GET.get('rating_id')
    token = request.GET.get('token')
    rating_instance = None

    if rating_id and token:
        rating_instance = get_object_or_404(Rating, id=rating_id, edit_token=token)

    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating_instance)
        if form.is_valid():
            if rating_instance and not form.has_changed():
                messages.info(request, "No changes detected.", extra_tags='rating')
            else:
                if not rating_instance:
                    new_rating = form.save(commit=False)
                    new_rating.edit_token = uuid.uuid4()
                    new_rating.save()
                    messages.success(request, "Thank you for your feedback!", extra_tags='rating')
                else:
                    form.save()
                    messages.success(request, "Your rating has been updated!", extra_tags='rating')
            return HttpResponseRedirect(request.path + '#rating-section')
        else:
            print("Form is invalid")
    else:
        form = RatingForm(instance=rating_instance)

    ratings = Rating.objects.all().order_by('-date')

    # Use the utility function to get location and weather data
    location_weather_info = get_location_and_weather(request, city_input=request.GET.get('city', ''))

    response = render(request, 'jaspreet/home.html', {
        'visitors': visitors,
        'visitor_count': visitor_count,
        'form': form,
        'ratings': ratings,
        'editing': rating_instance is not None,
        **location_weather_info  # Unpack the dictionary into the context
    })

    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


