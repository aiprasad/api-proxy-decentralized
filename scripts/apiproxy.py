import requests
import json
import os
from time import sleep

class ApigeeDeployer:
    def __init__(self, org_name, env_name, api_name, client_id, client_secret, base_url="https://apigee.googleapis.com"):
        self.org_name = org_name
        self.env_name = env_name
        self.api_name = api_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.token = None

    def authenticate(self):
        """
        Authenticate with Apigee and get an access token.
        """
        url = f"{self.base_url}/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(url, data=data)
        response.raise_for_status()
        self.token = response.json()["access_token"]

    def get_headers(self):
        """
        Return headers for API requests.
        """
        if not self.token:
            self.authenticate()
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def deploy_proxy(self, zip_file_path):
        """
        Deploy an API proxy to the specified environment.
        """
        # Upload the proxy
        url = f"{self.base_url}/v1/organizations/{self.org_name}/apis?action=import&name={self.api_name}"
        with open(zip_file_path, "rb") as f:
            files = {"file": (os.path.basename(zip_file_path), f, "application/octet-stream")}
            response = requests.post(url, headers=self.get_headers(), files=files)
        response.raise_for_status()

        revision = response.json()["revision"]
        print(f"Uploaded proxy revision: {revision}")

        # Undeploy existing proxy
        self.undeploy_proxy()

        # Deploy the proxy
        deploy_url = f"{self.base_url}/v1/organizations/{self.org_name}/environments/{self.env_name}/apis/{self.api_name}/revisions/{revision}/deployments"
        deploy_response = requests.post(deploy_url, headers=self.get_headers())
        deploy_response.raise_for_status()

        print(f"Deployed proxy revision {revision} to {self.env_name}")

    def undeploy_proxy(self):
        """
        Undeploy an existing proxy from the specified environment.
        """
        url = f"{self.base_url}/v1/organizations/{self.org_name}/environments/{self.env_name}/apis/{self.api_name}/deployments"
        response = requests.get(url, headers=self.get_headers())

        if response.status_code == 404:
            print("No existing deployments found.")
            return

        response.raise_for_status()
        deployments = response.json()
        for deployment in deployments.get("revision", []):
            revision = deployment["revision"]
            undeploy_url = f"{self.base_url}/v1/organizations/{self.org_name}/environments/{self.env_name}/apis/{self.api_name}/revisions/{revision}/deployments"
            undeploy_response = requests.delete(undeploy_url, headers=self.get_headers())
            undeploy_response.raise_for_status()
            print(f"Undeployed revision {revision} from {self.env_name}")

    def validate_proxy(self):
        """
        Validate the deployment by checking the API status.
        """
        url = f"{self.base_url}/v1/organizations/{self.org_name}/environments/{self.env_name}/apis/{self.api_name}/deployments"
        response = requests.get(url, headers=self.get_headers())
        response.raise_for_status()

        deployments = response.json()
        if deployments.get("revision"):
            print(f"Validation successful: {self.api_name} is deployed.")
        else:
            print("Validation failed: Proxy is not deployed.")

if __name__ == "__main__":
    # Replace with your Apigee organization details
    ORG_NAME = "your_org_name"
    ENV_NAME = "test"  # Replace with your environment
    API_NAME = "your_api_name"
    CLIENT_ID = "your_client_id"
    CLIENT_SECRET = "your_client_secret"
    ZIP_FILE_PATH = "path/to/your/proxy.zip"

    deployer = ApigeeDeployer(ORG_NAME, ENV_NAME, API_NAME, CLIENT_ID, CLIENT_SECRET)

    try:
        deployer.deploy_proxy(ZIP_FILE_PATH)
        sleep(10)  # Wait for deployment to complete
        deployer.validate_proxy()
    except Exception as e:
        print(f"Error: {e}")
