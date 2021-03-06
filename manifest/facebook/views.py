# -*- coding: utf-8 -*-
from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from manifest.facebook.utils import parse_signed_request
from social_auth.utils import setting

@csrf_exempt
def iframe(request, 
        template_name='facebook/iframe.html', 
        unliked_template_name=None,
        redirect_url=None,
        extra_context={}, *args, **kwargs):
    """
    Generic homepage view for facebook iframe tabs and canvases
    
    Provides a homepage view for Facebook iframe applications and page tabs. 
    Parses Facebook's signed_request and renders a template depends on
    like data. 
    
    :param template_name:
        String defining the name of the template. 
        Default is ``facebook/iframe.html``.

    :param unliked_template_name:
        String defining the name of the template if user has not liked 
        the Facebook Page yet. Default is ``None``.

    :param redirect_url:
        URL to redirect if user liked the page. Default is ``None``.

    :param extra_context:
        A dictionary containing extra variables that should be passed to 
        the rendered template.
        
    """
    liked = request.session.get('facebook_liked', False)
    signed_request = parse_signed_request(request.POST.get('signed_request'), 
                                            settings.FACEBOOK_API_SECRET)
    if signed_request:
        liked = signed_request.get('page', signed_request).get('liked')
        # Get user object who requested this page via Facebook iframe
        try:    
            user = User.objects.select_related().get(is_active=True, social_auth__provider='facebook', social_auth__uid=signed_request.get('user_id', None))
            if user.id is not request.user.id:
                return redirect('socialauth_begin', backend='facebook')
        except User.DoesNotExist:
            if request.user.is_authenticated():
                # Log out authenticated user who is not requested this page
                logout(request)
    request.session['facebook_liked'] = liked
    if not liked and unliked_template_name:
        template_name = unliked_template_name
    if liked and redirect_url:
        return redirect(redirect_url)
    extra_context.update({'liked': liked})
    return render_to_response(template_name, extra_context, context_instance=RequestContext(request))

@csrf_exempt
def canvas(request, 
            template_name='facebook/canvas.html', 
            url='//facebook.com',
            extra_context={}, *args, **kwargs):
    """
    Generic redirect view for facebook iframe application
    
    Provides a redirect view for Facebook iframe applications.
    Use for redirect from a canvas to a page tab or vise versa.
    
    :param template_name:
        String defining the name of the template. 
        Default is ``facebook/canvas.html``.

    :param url:
        URL of the page tab or canvas application. 
        Default is ``//facebook.com``.

    :param extra_context:
        A dictionary containing extra variables that should be passed to 
        the rendered template.
        
    """
    extra_context.update({'url': url})
    return render_to_response(template_name, extra_context, context_instance=RequestContext(request))
    