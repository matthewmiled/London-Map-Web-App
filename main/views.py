from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Area, Borough, LoggedVisitInstance
from .forms import UploadImageForm


# This is the custom form we have defined (which includes email address)
from .forms import NewUserForm

# Create your views here.


def homepage(request):
    
    boroughs = Borough.objects.all()

    boroughs = boroughs.order_by('borough_name')

    return render(request=request, 
                  template_name='main/homepage.html',
                  context={'boroughs':boroughs},
                  )



def borough_slug(request, borough_slug):
    
    boroughs = [c.borough_name for c in Borough.objects.all()]
    if borough_slug in boroughs:
        
        # We want to get directed to a borough page that lists all areas in that borough

        if request.user.is_authenticated:
            visitor = request.user.id

        else: 
            visitor = None
        
        matching_areas = Area.objects.filter(borough_name=borough_slug)

        instances = {}

        
        for area in matching_areas:
            try:
                instance = LoggedVisitInstance.objects.get(user=visitor, area=area)
            except LoggedVisitInstance.DoesNotExist:
                instance = None
            
            instances.update({area:instance})
        
        
        
        
        return render(request=request,
                      template_name='main/borough.html',
                      context={'areas':matching_areas,
                               'instances': instances,
                               'borough': borough_slug}
                      )
    
    return HttpResponse(f'{borough_slug} does not correspond to anything')



def area_slug(request, borough_slug, area_slug):

    exact_area = Area.objects.get(area_name=area_slug)

    if request.user.is_authenticated:
        visitor = request.user.id

    else: 
        visitor = None

    instance = LoggedVisitInstance.objects.filter(user=visitor, area=exact_area)
    
    upload_form = UploadImageForm()


    if request.method == "POST":

        uploaded_form = UploadImageForm(request.POST, request.FILES)
    
        if uploaded_form.is_valid():
            uploaded_data = uploaded_form.cleaned_data
            

            uploaded_image = uploaded_data['image']
            uploaded_image.name = f'{exact_area}.jpeg'

            uploaded_comment = uploaded_data['comment']

            LoggedVisitInstance.objects.create(
                user=request.user,
                area=exact_area,
                comment=uploaded_comment,
                image=uploaded_image)

            
            print(borough_slug)

            url = request.build_absolute_uri(f'/{borough_slug}')

            return redirect(url)
            
        elif request.POST['action'] == 'delete':
            LoggedVisitInstance.objects.filter(user=visitor, area=exact_area).delete()


    
    
    
    
    # This is just relating to the loading of the area.html page (get request)

    
    return render(request=request,
                  template_name='main/area.html',
                  context={'area': exact_area,
                           'visitor': visitor,
                           'instance': instance,
                           'form': upload_form}
                           )



def register(request):
    # We have defined a NewUserForm form in forms.py
    
    # Most requests are 'get' requests - the user just accesses 
    # stuff on the server/database
    
    # But if a user 'regsiters' and adds an email/password, they
    # need to add something to the server. This is a POST request
    
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            
            # This creates the success message, but doesn't display it
            # The actual message post code is written in header.html,
            # because it is the same process site-wide
            
            messages.success(request, f"New Account Created: {username}")
            
            # Default logs the user in once they have created an account, and creates an info message
            
            login(request, user)
            messages.info(request, f"You are now logged in as {username}")
            
            # Redirects back to main page if the register process is a success
            
            return redirect('main:homepage')
        
        else:
            for msg in form.error_messages:
                
                # If there is an error filling out the register for, the error message is made
                # but the message is not yet displayed
                
                messages.error(request, f"{msg}: {form.error_messages[msg]}")
            
    # This is just the 'get' request stuff for the register page
            
    form = NewUserForm
    return render(request=request, 
                  template_name="main/register.html",
                  context={"form":form})



def login_request(request):
    
    # If a user logs in, they need to add something to the server. 
    # This is a POST request  
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect("main:homepage")
            
            else:
                messages.error(request, "Invalid username or password")
                
        else:
            messages.error(request, "Invalid username or password")
        
    
    form = AuthenticationForm()
    return render(request=request,
                  template_name="main/login.html",
                  context={"form":form})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged Out")
    return redirect("main:homepage")
