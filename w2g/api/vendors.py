"""
entity resolution
"""

from configs import API_KEYS
#pip install --upgrade google-api-python-client

apis = {
    "wikidata": {
        "url": "https://www.wikidata.org/w/api.php",
        "params": lambda query, offset=0: {
            'format': 'json', 'language': 'en',
            'uselang': 'en', 'type': 'item',
            'search': query, 'continue': offset,
            "action": 'wbsearchentities'
        }
    },
    "google": {
        "url": "https://kgsearch.googleapis.com/v1/entities:search",
        "params": lambda query, limit=1: {
            "query": query, "key": API_KEYS.get('google', ''),
            "limit": limit, "indent": True
        }
    },
    "facebook": {
        "url": "https://graph.facebook.com/v2.5/search",
        "params": lambda query, fields: {
            'type': 'topic', 'q': query, 'fields': fields
        }
    },
    "stackoverflow": {
        "url": "https://api.stackexchange.com/2.2/tags",
        "params": {
            "order": "desc", "sort": "popular", "site": "stackoverflow"
        }
    },
    "openlibrary": {
        "url": "https://openlibrary.org/api/books",
        "params": lambda bibkeys: {
            "bibkeys": bibkeys  # csv: ISBN:XXXXXXXXXXXXX,ISBN:XX...
        }
    }
}
