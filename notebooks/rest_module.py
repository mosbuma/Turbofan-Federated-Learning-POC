import requests

class BearerAuth(requests.auth.AuthBase):
    """Bearer Token Authentication for Requests"""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Bearer {self.token}"
        print(f"Request headers: {r.headers}")
        return r


def make_rest_call(url, token):
    """Make a REST API call to a given URL using Bearer Token Authentication"""
    
    headers = {"Accept": "application/json"}
    response = requests.post(url, headers=headers, auth=BearerAuth(token))
    
    if response.status_code == 200:
        return response.json()
    else:
        print("got response status code ", response.status_code)
        return None