import requests
import json
import time


class AMdEX:
    def __init__(self, base_url="https://develop.amdex.dev"):
        self.base_url = base_url
        self._auth = None

    def get_version(self):
        try:
            result = requests.get(f"{self.base_url}/api/version")
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error retrieving version:", str(e))
            return None

    def authenticate(self, name, password_hash):
        try:
            result = requests.post(
                f"{self.base_url}/api/auth",
                headers={"Accept": "application/json"},
                json=json.dumps({"name": name, "password_hash": password_hash}),
            )
            result.raise_for_status()
            self._auth = result.json()
        except requests.exceptions.RequestException as e:
            print("Error authenticating:", str(e))
            self._auth = None

    def get_account_info(self):
        return self._auth

    def get_dataviews(self):
        try:
            result = requests.get(
                f"{self.base_url}/api/authenticated/dataviews",
                headers={
                    "Authorization": f"Bearer {self._auth['bearer_token']}",
                    "origin": self.base_url,
                },
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error retrieving dataviews:", str(e))
            return None

    def create_dataview(self, body={}):
        try:
            result = requests.post(
                f"{self.base_url}/api/authenticated/dataviews",
                headers={
                    "Authorization": f"Bearer {self._auth['bearer_token']}",
                    "origin": self.base_url,
                },
                json=json.dumps(body),
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error creating dataview:", str(e))
            return None

    def delete_dataview(self, dataview_uuid):
        try:
            result = requests.delete(
                f"{self.base_url}/api/authenticated/dataviews/{dataview_uuid}",
                headers={
                    "Authorization": f"Bearer {self._auth['bearer_token']}",
                    "origin": self.base_url,
                },
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error deleting dataview:", str(e))
            return None

    def get_policies(self, uuid=None):
        try:
            if uuid == None:
                result = requests.get(
                    f"{self.base_url}/api/authenticated/policies",
                    headers={
                        "Authorization": f"Bearer {self._auth['bearer_token']}",
                        "origin": self.base_url,
                    },
                )
            else:
                result = requests.get(
                    f"{self.base_url}/api/authenticated/policies/{uuid}",
                    headers={
                        "Authorization": f"Bearer {self._auth['bearer_token']}",
                        "origin": self.base_url,
                    },
                )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error retrieving policies:", str(e))
            return None

    def create_policy(self, body={}):
        try:
            result = requests.post(
                f"{self.base_url}/api/authenticated/policies",
                headers={
                    "Authorization": f"Bearer {self._auth['bearer_token']}",
                    "origin": self.base_url,
                },
                json=json.dumps(body),
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error creating policy:", str(e))
            return None

    def delete_policy(self, policy_uuid):
        try:
            result = requests.delete(
                f"{self.base_url}/api/authenticated/policies/{policy_uuid}",
                headers={
                    "Authorization": f"Bearer {self._auth['bearer_token']}",
                    "origin": self.base_url,
                },
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error deleting policy:", str(e))
            return None

    def get_jobs(self):
        try:
            result = requests.get(
                f"{self.base_url}/api/authenticated/jobs/{self._auth['account_uuid']}",
                headers={
                    "Authorization": f"Bearer {self._auth['bearer_token']}",
                    "origin": self.base_url,
                },
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error retrieving jobs:", str(e))
            return None

    def create_job(self, body={}):
        try:
            print(body)
            result = requests.post(
                f"{self.base_url}/api/authenticated/jobs/{self._auth['account_uuid']}",
                headers={
                    "Authorization": f"Bearer {self._auth['bearer_token']}",
                    "origin": self.base_url,
                },
                json=json.dumps(body),
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error creating job:", str(e))
            return None

    def append_job(self, job_uuid, policy_uuids=[]):
        try:
            record = {
                "type": "append",
                "job_uuid": job_uuid,
                "data": {"policy_uuids": policy_uuids},
            }
            result = requests.post(
                f"{self.base_url}/api/authenticated/jobs/{self._auth['account_uuid']}",
                headers={
                    "Authorization": f"Bearer {self._auth['bearer_token']}",
                    "origin": self.base_url,
                },
                json=json.dumps(record),
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error appending job:", str(e))
            return None

    def delete_jobs(self):
        try:
            result = requests.delete(
                f"{self.base_url}/api/authenticated/jobs/{self._auth['account_uuid']}",
                headers={
                    "Authorization": f"Bearer {self._auth['bearer_token']}",
                    "origin": self.base_url,
                },
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
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

    def get_auditlogs(self, job_uuid):
        try:
            result = requests.get(
                f"{self.base_url}/api/authenticated/auditlogs/{self._auth['account_uuid']}/{job_uuid}",
                headers={
                    "Authorization": f"Bearer {self._auth['bearer_token']}",
                    "origin": self.base_url,
                },
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error retrieving audit logs:", str(e))
            return None

    def create_auditlog(self, job_uuid, body={}):
        try:
            result = requests.post(
                f"{self.base_url}/api/authenticated/auditlogs/{self._auth['account_uuid']}/{job_uuid}",
                headers={
                    "Authorization": f"Bearer {self._auth['bearer_token']}",
                    "origin": self.base_url,
                },
                json=json.dumps(body),
            )
            result.raise_for_status()
            return result.json()
        except requests.exceptions.RequestException as e:
            print("Error creating audit log:", str(e))
            return None
