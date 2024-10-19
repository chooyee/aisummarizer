import requests
from util.pylogger import LogUtility
import sys, os
from config import GlobalConfig

class VaultSecret:
    def __init__(self):
        self.globalConfig = GlobalConfig()
        # Define your credentials
        self.client_id = self.globalConfig.CLIENT_ID
        self.client_secret = self.globalConfig.CLIENT_SECRET
        self.logger=LogUtility.get_logger("VaultSecret")

    def getOauth2Token(self):
        # Set up the request parameters
        url = "https://auth.idp.hashicorp.com/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "audience": "https://api.hashicorp.cloud"
        }
        try:
            # Make the request
            response = requests.post(url, headers=headers, data=data)
            # Extract the access token
            hcp_api_token = response.json().get('access_token')
            #self.logger.debug(hcp_api_token)
            return hcp_api_token
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise

    def GetSecrets(self, hcp_api_token):
        # Define the URL and headers
        url = "https://api.cloud.hashicorp.com/secrets/2023-06-13/organizations/008ad62f-071c-470d-820a-a4671118f25c/projects/0cc09eb2-e208-4365-8757-22eb65d48f87/apps/test/open"
        headers = {
            "Authorization": f"Bearer {hcp_api_token}"
        }
        try:
            # Make the GET request
            response = requests.get(url, headers=headers)
            json = response.json()
            #self.logger.debug(json)
            for secret in json["secrets"]:
                version = secret["version"]
                #self.logger.debug(f'{secret["name"]} : {version["value"]}');                
                setattr(self.globalConfig, secret["name"], version["value"])
        except Exception as e:
            self.logger.error(f'{sys._getframe().f_code.co_name}: {e}')
            raise

if __name__ == "__main__":
    vault = VaultSecret()
    token = vault.getOauth2Token()
    vault.GetSecrets(token)
    config = GlobalConfig()
    print(config.HF_KEY)