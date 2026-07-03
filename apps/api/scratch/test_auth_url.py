from google_auth_oauthlib.flow import Flow

from app.config import settings

client_config = {
    "web": {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "redirect_uris": [settings.google_redirect_uri],
    }
}

flow = Flow.from_client_config(
    client_config, scopes=["https://www.googleapis.com/auth/drive"]
)
flow.redirect_uri = settings.google_redirect_uri

authorization_url, state = flow.authorization_url(
    access_type="offline", include_granted_scopes="true", prompt="consent"
)

print("GENERATED AUTH URL:")
print(authorization_url)
