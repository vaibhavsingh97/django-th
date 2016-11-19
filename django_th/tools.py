# coding: utf-8
import arrow
import importlib
import datetime
import time

from django.conf import settings
from django.core.mail import send_mass_mail


"""
    Simple utility functions
"""


def class_for_name(module_name, class_name):
    """
        Import a class dynamically
        :param module_name: the name of a module
        :param class_name: the name of a class
        :type module_name: string
        :type class_name: string
        :return: Return the value of the named attribute of object.
        :rtype: object
    """
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c


def get_service(service, model_form='models', form_name=''):
    """
        get the service name then load the model
        :param service: the service name
        :param model_form: could be 'models' or 'forms'
        :param form_name: the name of the form is model_form is 'forms'
        :type service: string
        :type model_form: string
        :type form_name: string
        :return: the object of the spotted Class.
        :rtype: object

        :Example:

        class_name could be :
            th_rss.models
            th_rss.forms
        service_name could be :
            ServiceRss
        then could call :
            Rss+ProviderForm
            Evernote+ConsumerForm
    """
    service_name = str(service).split('Service')[1]

    class_name = 'th_' + service_name.lower() + '.' + model_form

    if model_form == 'forms':
        return class_for_name(class_name, service_name + form_name)
    else:
        return class_for_name(class_name, service_name)


def to_datetime(data):
    """
        convert Datetime 9-tuple to the date and time format
        feedparser provides this 9-tuple
        :param data: data to be checked
        :type data: dict
    """
    my_date_time = None

    if 'published_parsed' in data:
        my_date_time = datetime.datetime.utcfromtimestamp(
            time.mktime(data.get('published_parsed')))
    elif 'created_parsed' in data:
        my_date_time = datetime.datetime.utcfromtimestamp(
            time.mktime(data.get('created_parsed')))
    elif 'updated_parsed' in data:
        my_date_time = datetime.datetime.utcfromtimestamp(
            time.mktime(data.get('updated_parsed')))
    elif 'my_date' in data:
        my_date_time = arrow.get(data['my_date'])

    return my_date_time


def warn_user_and_admin(consumer_provider, service):

    from_mail = settings.ADMINS if len(settings.ADMINS) > 0 else ''
    from_mail = settings.MANAGERS if len(settings.MANAGERS) > 0 else ''
    if len(from_mail) == 0:
        from_mail = settings.DEFAULT_FROM_EMAIL

    if consumer_provider == 'provider':
        service_name = service.provider.name.name.split('Service')[1]
    else:
        service_name = service.consumer.name.name.split('Service')[1]

    title = 'Trigger {} disabled'.format(service.description)
    body = 'The trigger "{}" has been disabled due to an issue with {}. ' \
           'Try to renew it to refresh the token to try to fix the issue'. \
        format(service.description, service_name)
    # for enduser
    message1 = (title,
                body,
                from_mail,
                [service.user.email])
    # for admin

    message2 = (title,
                body,
                from_mail,
                [from_mail])
    # send the two mails

    send_mass_mail((message1, message2), fail_silently=False)
