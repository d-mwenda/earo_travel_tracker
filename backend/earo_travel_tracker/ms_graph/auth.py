import msal

client_id = None
client_secret = None
authority = None
username = None
password = None
scopes = "https://graph.microsoft.com/.default",
list_id = None
site_id = None
vaccination_status_list_id = None

def authenticate_on_azure():
    """Instantiate an msal public application and get an authentication/authorization token to be used for http requests using
    Microsoft Graph API.
    """
    pub_app = msal.PublicClientApplication(client_id, authority=authority)
    # TODO Error handling
    token = pub_app.acquire_token_by_username_password(username, password, scopes, claims_challenge=None)
    return token

def validate_token(token):
    pass
