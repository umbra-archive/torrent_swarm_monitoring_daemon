from urllib.parse import urljoin, urlunparse, urlparse
from urllib.parse import urlparse

from .config_loader import config


def get_scheme_and_hostname(url):
    parsed_url = urlparse(url)
    url = f"{parsed_url.scheme}://{parsed_url.hostname}"
    return sanitize_url(url)

def sanitize_url(url):
    # "http://username:password@example.com/path?query=123#anchor"
    # becomes: "http://example.com/path"
    parsed = urlparse(url)
    sanitized = parsed._replace(
        netloc=parsed.hostname, params="", query="", fragment=""
    )
    return urlunparse(sanitized)

class Collection():
    def __init__(self, name):
        self.name = name
        self.enabled = config["collection"][name]["enabled"]

        if "required_substring" in config["collection"][name]:
            self.required_substring = config["collection"][name]["required_substring"]
        else:
            self.required_substring = None

        url = config["collection"][name]["torrent_url"]
        self.url = sanitize_url(url)

    def debug(self):
        print(f"[name:    {self.name}")
        print(f" url:     {self.url}")
        print(f" enabled: {self.enabled}]")
