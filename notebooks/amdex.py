import requests
import json
import time


class AMdEX:
    def __init__(self, base_url="https://develop.trust.amdex.dev"):
        self.base_url = base_url
        self._requestsSession = requests.Session()
        self._session = None

    def get_version(self):
        try:
            result = self._requestsSession.get(f"{self.base_url}/api/version")
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error retrieving version:", str(e))
            return None

    def signin(self, email, password_hash):
        try:
            # Fetch CSRF token
            result1 = self._requestsSession.get(f"{self.base_url}/api/auth/csrf")
            result1.raise_for_status()
            csrf_token = result1.json()["csrfToken"]

            # Prepare credentials
            credentials = {
                "csrfToken": csrf_token,
                "email": email,
                "password_hash": password_hash,
                "json": "true",
            }

            # Make authentication request
            result2 = self._requestsSession.post(
                f"{self.base_url}/api/auth/callback/credentials",
                headers={"Content-Type": "application/json"},
                json=credentials,
            )
            result2.raise_for_status()

            # Fetch session if authentication was successful
            if result2.ok:
                result3 = self._requestsSession.get(f"{self.base_url}/api/auth/session")
                result3.raise_for_status()
                session = result3.json()
                self._session = session["user"] if "user" in session else None

        except requests.exceptions.RequestException as e:
            print("Error during sign in:", str(e))
            self._session = None

    def get_session(self):
        return self._session

    def get_dataviews(self):
        try:
            result = self._requestsSession.get(
                f"{self.base_url}/api/authenticated/dataviews",
            )
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error retrieving dataviews:", str(e))
            return None

    def create_dataview(self, body={}):
        try:
            result = self._requestsSession.post(
                f"{self.base_url}/api/authenticated/dataviews",
                json=json.dumps(body),
            )
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error creating dataview:", str(e))
            return None

    def delete_dataview(self, dataview_uuid):
        try:
            result = self._requestsSession.delete(
                f"{self.base_url}/api/authenticated/dataviews/{dataview_uuid}",
            )
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error deleting dataview:", str(e))
            return None

    def get_policies(self, uuid=None):
        try:
            if uuid == None:
                result = self._requestsSession.get(
                    f"{self.base_url}/api/authenticated/policies",
                )
            else:
                result = self._requestsSession.get(
                    f"{self.base_url}/api/authenticated/policies/{uuid}",
                )
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error retrieving policies:", str(e))
            return None

    def create_policy(self, body={}):
        try:
            result = self._requestsSession.post(
                f"{self.base_url}/api/authenticated/policies",
                json=json.dumps(body),
            )
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error creating policy:", str(e))
            return None

    def delete_policy(self, policy_uuid):
        try:
            result = self._requestsSession.delete(
                f"{self.base_url}/api/authenticated/policies/{policy_uuid}",
            )
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error deleting policy:", str(e))
            return None

    def get_jobs(self):
        try:
            result = self._requestsSession.get(
                f"{self.base_url}/api/authenticated/jobs",
            )
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error retrieving jobs:", str(e))
            return None

    def create_job(self, body={}):
        try:
            print(body)
            result = self._requestsSession.post(
                f"{self.base_url}/api/authenticated/jobs",
                json=json.dumps(body),
            )
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error creating job:", str(e))
            return None

    def delete_jobs(self):
        try:
            result = self._requestsSession.delete(
                f"{self.base_url}/api/authenticated/jobs",
            )
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error deleting jobs:", str(e))
            return None

    def poll_job_status(
        self,
        job_uuid,
        max_total_interval=5 * 1000,
        initial_interval=100,
        interval_increase=200,
    ):
        total_interval = 0
        interval = initial_interval

        while True:
            existing_jobs = self.get_jobs()
            job = next((j for j in existing_jobs if j["job_uuid"] == job_uuid), None)

            if job:
                if job["status"] == "OK":
                    return True
                if job["status"] == "FAILED":
                    return False

            if total_interval >= max_total_interval:
                break

            total_interval += interval
            time.sleep(interval / 1000)
            interval += interval_increase

        return None

    def get_notary_lines(self, job_uuid):
        try:
            result = self._requestsSession.get(
                f"{self.base_url}/api/authenticated/notary/{job_uuid}",
            )
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error retrieving audit logs:", str(e))
            return None

    def create_notary_line(self, job_uuid, body={}):
        try:
            result = self._requestsSession.post(
                f"{self.base_url}/api/authenticated/notary/{job_uuid}",
                json=json.dumps(body),
            )
            result.raise_for_status()
            return result.json()
        except self._requestsSession.exceptions.RequestException as e:
            print("Error creating notary line:", str(e))
            return None
