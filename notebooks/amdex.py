import requests
import time


def fetchAuth(name, password_hash):
    result = requests.post(
        "http://localhost:3002/api/auth",
        json={"name": name, "password_hash": password_hash},
    )
    return result.json()


def fetchJobs(account_uuid, bearer_token, body={}):
    url = f"http://localhost:3002/api/authenticated/jobs/{account_uuid}"
    method = "GET" if not body else "POST"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "origin": "http://localhost:3002",
    }
    result = requests.request(method, url, headers=headers, json=body)
    return result.json()


def pollJobStatus(
    account_uuid,
    job_uuid,
    bearer_token,
    maxTotalInterval=5 * 1000,
    initialInterval=100,
    intervalIncrease=200,
):
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


def fetchAuditlogs(account_uuid, job_uuid, bearer_token, body={}):
    url = f"http://localhost:3002/api/authenticated/auditlogs/{account_uuid}/{job_uuid}"
    method = "GET" if not body else "POST"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "origin": "http://localhost:3002",
    }
    result = requests.request(method, url, headers=headers, json=body)
    return result.json()


def fetchDataviews(account_uuid, bearer_token, method="GET", body={}):
    url = "http://localhost:3002/api/authenticated/dataviews"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "origin": "http://localhost:3002",
    }
    result = requests.request(method, url, headers=headers, json=body)
    return result.json()


def fetchApi(api_function):
    result = requests.get(f"http://localhost:3002/api/{api_function}")
    return result.json()
