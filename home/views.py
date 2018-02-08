# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from django.contrib.auth.models import User
from django.template import loader, RequestContext
from datetime import date

 
def index(request):
    context = {}
    return render(request, 'home/index.html', context)
