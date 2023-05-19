import requests
import json
import time

class AMdEX:
    def __init__(self, base_url="https://develop.amdex.dev"):
        self.base_url = base_url
        self._auth = None

    def getAccountInfo(self):
        return self._auth

    def authenticate(self, name, password_hash):
        try:
            print("got base url", self.base_url)
            result = requests.post(
                f"{self.base_url}/api/auth",
                headers={"Accept": "application/json"},
                json=json.dumps({"name": name, "password_hash": password_hash}),
            )
            # result.raise_for_status()
            self._auth = result.json()
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")

    @property
    def version(self):
        def get():
            try:
                result = requests.get(f"{self.base_url}/api/version")
                result.raise_for_status()
                return result.json()
            except requests.exceptions.RequestException as e:
                print(f"Failed to retrieve version info: {e}")
                return None

        return {"get": get}

    @property
    def dataviews(self):
        def get():
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
                print(f"Failed to retrieve dataviews: {e}")
                return None

        def post(body={}):
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
                print(f"Failed to create dataview: {e}")
                return None

        def delete(dataview_uuid):
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
                print(f"Failed to delete dataview: {e}")
                return None

        return {"get": get, "post": post, "delete": delete}

    @property
    def policies(self):
        def get():
            try:
                result = requests.get(
                    f"{self.base_url}/api/authenticated/policies",
                    headers={
                        "Authorization": f"Bearer {self._auth['bearer_token']}",
                        "origin": self.base_url,
                    },
                )
                result.raise_for_status()
                return result.json()
            except requests.exceptions.RequestException as e:
                print(f"Failed to retrieve policies: {e}")
                return None

        def post(body={}):
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
                print(f"Failed to create policy: {e}")
                return None

        def delete(policy_uuid):
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
                print(f"Failed to delete policy: {e}")
                return None

        return {"get": get, "post": post, "delete": delete}

    @property
    def jobs(self):
        def get():
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
                print(f"Failed to retrieve jobs: {e}")
                return None

        def post(body={}):
            try:
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
                print(f"Failed to create job: {e}")
                return None

        def delete():
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
                print(f"Failed to delete jobs: {e}")
                return None

        return {"get": get, "post": post, "delete": delete}
