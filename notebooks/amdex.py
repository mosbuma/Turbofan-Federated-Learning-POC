import requests
import time
import json

BASE_URL = "https://develop.amdex.dev"


# class BearerAuth(requests.auth.AuthBase):
#     """Bearer Token Authentication for Requests"""

#     def __init__(self, token):
#         self.token = token

#     def __call__(self, r):
#         r.headers["Authorization"] = f"Bearer {self.token}"
#         print(f"Request headers: {r.headers}")
#         return r


# def make_rest_call(url, token):
#     """Make a REST API call to a given URL using Bearer Token Authentication"""

#     headers = {"Accept": "application/json"}
#     response = requests.post(url, headers=headers, auth=BearerAuth(token))

#     if response.status_code == 200:
#         return response.json()
#     else:
#         print("got response status code ", response.status_code)
#         return None


def fetchAuth(name, password_hash):
    try:
        url = f"{BASE_URL}/api/auth"
        jsonobj = {
            "name": name,
            "password_hash": password_hash,
        }

        print("fetchAuth - url:" + url, flush=True)
        print("fetchAuth - password_hash:" + password_hash, flush=True)
        print("fetchAuth - json:" + json.dumps(jsonobj), flush=True)

        headers = {"Accept": "application/json"}
        result = requests.post(
            url,
            headers=headers,
            json=json.dumps(jsonobj),
        )
        result.raise_for_status()
        return result.json()
    except requests.exceptions.RequestException as e:
        print("Error during fetchAuth:", e)
        return None


def fetchJobs(account_uuid, bearer_token, body={}):
    try:
        url = f"{BASE_URL}/api/authenticated/jobs/{account_uuid}"
        method = "GET" if not body else "POST"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "origin": BASE_URL,
        }
        result = requests.request(method, url, headers=headers, json=body)
        result.raise_for_status()
        return result.json()
    except requests.exceptions.RequestException as e:
        print("Error during fetchJobs:", e)
        return None


def pollJobStatus(
    account_uuid,
    job_uuid,
    bearer_token,
    maxTotalInterval=5 * 1000,
    initialInterval=100,
    intervalIncrease=200,
):
    try:
        totalInterval = 0
        interval = initialInterval

        while True:
            jobs = fetchJobs(account_uuid, bearer_token)
            job = next((job for job in jobs if job["job_uuid"] == job_uuid), None)

            if job:
                if job["status"] == "OK":
                    return True
                if job["status"] == "FAILED":
                    return False

            if totalInterval >= maxTotalInterval:
                return None

            totalInterval += interval
            time.sleep(interval / 1000)
            interval += intervalIncrease

        return None
    except Exception as e:
        print("Error during pollJobStatus:", e)
        return None


def fetchAuditlogs(account_uuid, job_uuid, bearer_token, body={}):
    try:
        url = f"{BASE_URL}/api/authenticated/auditlogs/{account_uuid}/{job_uuid}"
        method = "GET" if not body else "POST"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "origin": BASE_URL,
        }
        result = requests.request(method, url, headers=headers, json=body)
        result.raise_for_status()
        return result.json()
    except requests.exceptions.RequestException as e:
        print("Error during fetchAuditlogs:", e)
        return None


def fetchDataviews(account_uuid, bearer_token, method="GET", body={}):
    try:
        url = f"{BASE_URL}/api/authenticated/dataviews"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "origin": BASE_URL,
        }
        result = requests.request(method, url, headers=headers, json=body)
        result.raise_for_status()
        return result.json()
    except requests.exceptions.RequestException as e:
        print("Error during fetchDataviews:", e)
        return None


def fetchApi(api_function):
    try:
        result = requests.get(f"{BASE_URL}/api/{api_function}")
        result.raise_for_status()
        return result.json()
    except requests.exceptions.RequestException as e:
        print("Error during fetchApi:", e)
        return None
