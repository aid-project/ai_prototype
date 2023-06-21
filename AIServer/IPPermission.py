"""
simple middlware to block IP addresses via settings 
variable BLOCKED_IPS
"""
from rest_framework import permissions
from django.conf import settings
from django import http

class SafeIPPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if ip := request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = ip.split(',')[-1]
        else:
            ip = request.META.get('REMOTE_ADDR')
        print(ip)
        return ip in settings.ALLOWED_HOSTS
