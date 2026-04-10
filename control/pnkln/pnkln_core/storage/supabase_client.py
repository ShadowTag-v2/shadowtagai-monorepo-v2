import os
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """ Initializes and returns a Supabase client using environment variables.

    Raises:
        ValueError: If Supabase URL or Key is not set in the environment.

    Returns:
        An authenticated Supabase client instance.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set.")
    return create_client(url, key)
