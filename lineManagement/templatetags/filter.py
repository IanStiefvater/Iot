from django import template
from django.shortcuts import get_object_or_404
import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from lineManagement.controllers.device_details.details import get_ph
from lineManagement.models import device_production, lines

register = template.Library()


@register.filter(name="get_item")
def get_item(dictionary, key):
    result = dictionary.get(key)
    return result
