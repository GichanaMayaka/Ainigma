import logging

import pygeoip
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from ipware import ip

import settings
from forms import ResponseForm, UserForm, UserProfileForm
from models import Survey, Category
from settings import gi

# Global counter flag
counter = 0

# Logging configuration
logging.basicConfig(filename='project_log.txt', level=logging.DEBUG, format = '%(asctime)s - %(levelname)s - %('
                                                                              'message)s')
logging.debug('Start of Application')

gi = pygeoip.GeoIP(gi)


def locate(rec):
    logging.debug('Start of __IP Location__')
    # Geo-location function
    ip_address = (ip.get_ip(rec)).strip()
    if ip_address == '127.0.0.1':
        return 'Kenya'

    else:
        q_object = gi.record_by_addr(ip_address)
        try:
            country = q_object['country_name']
            logging.debug('Value of country is: {}'.format(country))
            return country
        except pygeoip.GeoIPError as e:
            logging.debug('Error message: {}'.format(e))
            pass


def index(request):
    return render(request, 'index.html')


def survey_list(request):
    surveys = Survey.objects.all()
    return render(request, 'survey_list.html', {'surveys': surveys})


@login_required
def survey_detail(request, survey_id):
    global counter
    survey = Survey.objects.get(id=survey_id)
    category_items = Category.objects.filter(survey=survey)
    categories = [c.category_name for c in category_items]
    logging.debug('\t\t\t\tCategories\n')
    logging.debug('Categories for this survey')
    logging.debug('Categories are: {}\n'.format(categories))

    if request.method == 'POST':
        if counter < 1:
            form = ResponseForm(request.POST, survey=survey)

            if form.is_valid():
                response = form.save()
                response.country = locate(request)
                response.save()

                counter += 1
                logging.debug('Value of counter is: {}'.format(counter))
                return HttpResponseRedirect("/confirm/%s" % response.interview_uuid)

        else:
            return HttpResponse('/participation.html/')

    else:
        form = ResponseForm(survey=survey)
        logging.debug('form print: {}'.format(form))

    return render(request, 'survey.html', {'response_form': form, 'survey': survey, 'categories': categories})


@login_required
def confirm(request, uuid):
    email = settings.support_email
    return render(request, 'confirm.html', {'uuid': uuid, "email": email})


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES.get('profile_picture')

            profile.save()
            registered = True
            return HttpResponseRedirect('/home/')

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'register.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/home/')

            else:
                return HttpResponse('Your account is disabled')
        else:
            return HttpResponse('Invalid Login Details')

    else:
        return render(request, 'login.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/home/')
