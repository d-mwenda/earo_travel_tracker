"""
Various context processors for the traveler app.
"""
from guardian.shortcuts import get_perms

def get_nav_menu_items(request):
    """
    Get the navigation menu links to be displayed to users to only show
    the items user has appropriate permissions to.
    """
    user = request.user
    nav_menu = dict()
    nav_menu['trip']= "present"
    return nav_menu
