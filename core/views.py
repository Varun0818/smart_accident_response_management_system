from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
import requests
from .models import AccidentReport
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import ResponderLocation

@csrf_exempt
def api_accept(request):
    if request.method == 'PATCH':
        if 'hospital_name' not in request.session:
            return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)
        data = json.loads(request.body)
        report_id = data.get('report_id')
        hospital_name = request.session['hospital_name']  # Always use this key!
        report = get_object_or_404(AccidentReport, id=report_id)
        report.status = 'enroute'
        report.assigned_hospital = hospital_name
        report.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def api_reject(request):
    if request.method == "DELETE":
        data = json.loads(request.body)
        report_id = data.get("report_id")
        AccidentReport.objects.filter(id=report_id).delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@csrf_exempt
def api_resolve(request):
    if request.method == "PATCH":
        data = json.loads(request.body)
        report_id = data.get("report_id")
        report = AccidentReport.objects.get(id=report_id)
        report.status = "resolved"
        report.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

@csrf_exempt
def update_responder_location(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        rl, created = ResponderLocation.objects.update_or_create(
            user=request.user,
            defaults={'latitude': latitude, 'longitude': longitude}
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'unauthorized'}, status=401)

# --- HAVERSINE DISTANCE (km) ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# --- TRACKING PAGE VIEW ---
def tracking_view(request, report_id):
    report = get_object_or_404(AccidentReport, id=report_id)
    try:
        responder = ResponderLocation.objects.get(user=report.assigned_responder)
        distance_km = haversine(report.latitude, report.longitude, responder.latitude, responder.longitude)
    except (ResponderLocation.DoesNotExist, AttributeError):  # AttributeError if assigned_responder missing
        responder = None
        distance_km = None

    context = {
        'report': report,
        'responder': responder,
        'distance_km': f"{distance_km:.2f}" if distance_km else "--",
        'eta_min': f"{(distance_km/0.833):.0f}" if distance_km else "--"  # Assumes avg 50 km/h (0.833 km/min)
    }
    return render(request, 'tracking.html', context)



# --- Firestore imports have been removed ---
import os
import math # Import math for distance calculation

def home(request):
    """
    Renders the home page with options to login as Reporter or Responder.
    """
    return render(request, 'core/home.html')
def report_accident(request):
    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        severity = request.POST.get('severity', '')
        lat_str = request.POST.get('latitude', '')
        lng_str = request.POST.get('longitude', '')
        image = request.FILES.get('image', None)

        errors = []
        # Location Validation
        if not lat_str or not lng_str or lat_str in ('0', '') or lng_str in ('0', ''):
            errors.append("Accident location must be selected on the map.")
        # Severity Validation
        if not severity:
            errors.append("Please select the accident severity.")
        # Description Validation
        if not description:
            errors.append("Description is required.")

        # Convert to float safely
        try:
            latitude = float(lat_str)
            longitude = float(lng_str)
        except ValueError:
            errors.append("Invalid latitude or longitude value.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'report_form.html')

        # Save report
        report = AccidentReport(
            description=description,
            severity=severity,
            latitude=latitude,
            longitude=longitude
        )

        if image:
            report.image = image

        report.save()
        messages.success(request, "Your report has been submitted successfully!")
        return redirect('home')  # or wherever you redirect on success

    # GET request
    return render(request, 'report_form.html')

def reporter_login(request):
    """
    Handles the reporter login. Saves name and phone to session.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        
        # Store in session for later use
        request.session['reporter_name'] = name
        request.session['reporter_phone'] = phone
        
        return redirect('report_accident')
    
    return render(request, 'core/reporter/login.html')

def report_accident(request):
    """
    Handles the submission of a new accident report.
    """
    # Check if user is "logged in" via session
    if 'reporter_name' not in request.session:
        messages.error(request, 'Please log in as a reporter first.')
        return redirect('reporter_login')
    
    if request.method == 'POST':
        # Get form data
        reporter_name = request.session.get('reporter_name')
        phone = request.session.get('reporter_phone')
        latitude = float(request.POST.get('latitude'))
        longitude = float(request.POST.get('longitude'))
        description = request.POST.get('description')
        severity = request.POST.get('severity')
        
        # Handle image upload
        image = None
        if request.FILES.get('image'):
            image = request.FILES['image']
        
        # Create report in Django DB (SQLite)
        try:
            report = AccidentReport.objects.create(
                reporter_name=reporter_name,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                description=description,
                severity=severity,
                image=image,
                status='reported'
            )
            
            # Call find_nearby_hospitals AFTER creating the report
            # This function will now only update the Django DB
            find_nearby_hospitals(latitude, longitude, report.id)
            
            # Redirect to tracking page
            return redirect('reporter_tracking', report_id=report.id)
        
        except Exception as e:
            print(f"Error creating report: {e}")
            messages.error(request, f"An error occurred while creating the report: {e}")
            return render(request, 'core/reporter/report_form.html')
    
    return render(request, 'core/reporter/report_form.html')

def reporter_tracking(request, report_id):
    """
    Displays the status of a reported accident for the reporter.
    """
    report = get_object_or_404(AccidentReport, id=report_id)
    return render(request, 'core/reporter/tracking.html', {'report': report})

def responder_login(request):
    """
    Handles the responder login. Saves name and phone to session (no password).
    """
    # --- THIS FUNCTION IS NOW MODIFIED ---
    if request.method == 'POST':
        # Get name and phone, just like the reporter
        name = request.POST.get('name') 
        phone = request.POST.get('phone')
        
        # Store in session for later use
        request.session['name'] = name
        request.session['responder_phone'] = phone
        request.session['hospital_name'] = name
        # No password check, just redirect to the dashboard
        return redirect('responder_dashboard')
        
    # We still render the login.html, but you must
    # update login.html to ask for "Name" and "Phone"
    return render(request, 'core/responder/login.html')

def responder_dashboard(request):
    """
    Displays the dashboard for logged-in responders.
    """
    # Check if responder is "logged in" via session
    if 'name' not in request.session:
        messages.error(request, 'Please log in as a responder first.')
        return redirect('responder_login')
    
    # Get active reports (not resolved)
    active_reports = AccidentReport.objects.exclude(status='resolved').order_by('-timestamp')
    
    return render(request, 'core/responder/dashboard.html', {'reports': active_reports})

def case_detail(request, report_id):
    """
    Displays the detailed view of a single accident case for a responder.
    """
    # Check if responder is "logged in" via session
    if 'name' not in request.session:
        return redirect('responder_login')
    
    report = get_object_or_404(AccidentReport, id=report_id)
    
    return render(request, 'core/responder/case_detail.html', {'report': report})

@csrf_exempt
def api_report(request):
    """
    API endpoint for submitting a report (e.g., from a mobile app).
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create report in Django DB
            report = AccidentReport.objects.create(
                reporter_name=data.get('reporter_name'),
                phone=data.get('phone'),
                latitude=data.get('lat'),
                longitude=data.get('lon'),
                description=data.get('description'),
                severity=data.get('severity'),
                status='reported'
            )
            
            # Find nearby hospitals
            find_nearby_hospitals(data.get('lat'), data.get('lon'), report.id)
            
            return JsonResponse({'status': 'success', 'report_id': report.id})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



def find_nearby_hospitals(lat, lon, report_id):
    """
    Finds nearby hospitals using Google Maps API and updates the report.
    This function now ONLY updates the Django DB (SQLite).
    """
    try:
        from django.conf import settings
        
        # Check if API key is present
        if not hasattr(settings, 'GOOGLE_MAPS_API_KEY') or not settings.GOOGLE_MAPS_API_KEY:
            print("GOOGLE_MAPS_API_KEY not set in settings.py. Skipping hospital search.")
            # Set status to alerted anyway so the flow can continue
            report = AccidentReport.objects.get(id=report_id)
            report.status = 'alerted'
            report.save()
            return

        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lon}",
            "radius": 5000, # 5km radius
            "type": "hospital",
            "key": settings.GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Error from Google Maps API: {response.text}")
            return

        hospitals = response.json().get("results", [])
        
        report = AccidentReport.objects.get(id=report_id)
        
        if hospitals:
            # Get the first hospital (closest one)
            first_hospital = hospitals[0]
            hospital_name = first_hospital.get('name', 'Nearby Hospital')
            
            # --- Example of getting distance/ETA ---
            # This would require another API call to Distance Matrix API
            # For simplicity, we just assign the hospital for now.
            # report.assigned_hospital = hospital_name 
            # We will let the responder assign themselves.
            
            # For demo, let's just log the nearby hospitals
            print(f"Nearby hospitals found: {[h.get('name') for h in hospitals]}")

        # Update report status to 'alerted' so responders can see it
        report.status = 'alerted'
        report.save()
        
    except Exception as e:
        print(f"Error in find_nearby_hospitals: {e}")

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points in km using Haversine formula.
    """
    # Approximate radius of earth in km
    R = 6371.0
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    
    return round(distance, 1)

