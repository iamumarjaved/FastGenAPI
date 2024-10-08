from authlib.integrations.starlette_client import OAuth
from src.core.config import settings

oauth = OAuth()
oauth.register(
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name='github',
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    authorize_url=settings.github_authorize_url,
    access_token_url=settings.github_token_url,
    client_kwargs={'scope': 'read:user'}
)

oauth.register(
    name='facebook',
    client_id=settings.facebook_client_id,
    client_secret=settings.facebook_client_secret,
    authorize_url=settings.facebook_authorize_url,
    access_token_url=settings.facebook_token_url,
    client_kwargs={'scope': 'email'}
)
