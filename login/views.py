# Import the required django functions
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

# Helper functions
from .functions import getInformation, testToken, check_friend

# The main view nginx uses to authenticate
# Returns HTTP status 201 if the user is authenticated, if not it returns HTTP status 401.
def authentication(request):

    # Try to get the authentication token
    try:
        token = request.session['plexjocke_token']

        # If there is a token and it is valid tell nginx the user is authenticated.
        if token:
            return HttpResponse(status=201)
    # If there's no token, reject the user.
    except KeyError:
        return HttpResponse(status=401)


# Handles sign in functionality.
def login(request):

    # Try and get the return url, if it doesn't exist set a placeholder url.
    try:
        redirect_url = request.GET['return']
    except KeyError:
        redirect_url = 'plex.nit13.se'

    # Reset the login error.
    login_error = False

    # Try to get the authentication token.
    try:
        token = request.session['plexjocke_token']

        # Return the user to the page they came from if they are already authentcated.
        if token and testToken(token):
            return HttpResponseRedirect('https://' + redirect_url)
    # Authenticate if there is no token.
    except KeyError:
        # Try and get the username and password to authencate
        try:
            username = request.POST['username']
            password = request.POST['password']

            # Get the authenticati token of that user.
            information = getInformation(username, password)

            # If there's a valid token and the user is on the friends list try to authenticate the user.
            if information != None and check_friend(username):
                try:
                    # If the user checked the remember me checkbox the session shouldn't expire when the browser closes.
                    remember_me = request.POST['rememberMe']
                    if remember_me:
                        settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
                # If the user didn\t check the remember me checkbox the session should expire when the browser is closed.
                except KeyError:
                    settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True

                # Set the users current session variables.
                request.session['plexjocke_token'] = information[0]
                request.session['plexjocke_username'] = username
                request.session['plexjocke_email'] = information[1]

                # Return the user to the last page they visited.
                return HttpResponseRedirect('https://' + redirect_url)
            else:
                # If the user entered incorrect information set the login error to true.
                login_error = True

        # Do nothing if the user didn't enter all information required, this is handled by javascript.
        except KeyError:
            pass

        # Pass the login error to the page.
        context = {
            'loginError': login_error,
        }

        # Render the page
        return render(request, 'login/login.html', context)


# View for signing out
def logout(request):
    # Try and get the return url, if there's none set a placeholder url
    try:
        redirect_url = request.GET['return']
    except KeyError:
        redirect_url = 'plex.nit13.se'

    # Try to remove the session
    try:
        del request.session['plexjocke_token']
        del request.session['plexjocke_username']
        del request.session['plexjocke_email']
    except KeyError:
        pass

    # Return the suer to the previous page.
    return HttpResponseRedirect('https://' + redirect_url)
