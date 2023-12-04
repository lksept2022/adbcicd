import os
import requests
from requests.exceptions import HTTPError  


from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient


# TODO: duplicate from reference pipeline.library.helper.spn

def generate_spn_ad_token(tenant_id: str, spn_client_id: str, spn_client_secret: str) -> str:
    """
    Generate a short lived AD tokon for a specific SPN.

    :param tenant_id: the Azure tenant id
    :param spn_client_id: the service principal client id
    :param spn_client_secret: the service principal client secret
    :retun: the generated AD tocken for the service principal
    """

    req = requests.post(
        f"https://login.microsoftonline.com/{tenant_id}/oathu2/v2.0/token",

        headers={
            "Content-Type" : "application/x-www-form-urlencoded"
        },
        data = {
            "client_id" : spn_client_id,
            "grant_type" : "client_credentials",
            "scope" : "dfdfdfdf/.default",
            "client_secret" : spn_client_secret
        }
    )

    try:
        req.raise_for_status()

    except HTTPError as e:
        print(e.response.text)
        raise e
    
    return req.json()["access_token"]


def delete_adls_folder(storage_account: str, container: str, folder_path: str):
    """
    Delete an ADLS Gen2 folder via service principal.
    
    NB: 3 environment variables must be present when this function is run:
    AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET

    NB: We don't raise an error when the folder path doesn't exist in the container.

    :param storage_account: ADLS Gen 2 storage account name
    :param container: ADLS Gen 2 container name
    :param folder_path: path of the folder to delete within the container

    """

    assert "AZURE_TENANT_ID" in os.environ, "'AZURE_TENANT_ID' must be an environment variable"
    assert "AZURE_CLIENT_ID" in os.environ, "'AZURE_CLIENT_ID' must be an environment variable"
    assert "AZURE_CLIENT_SECRET" in os.environ, "'AZURE_CLIENT_SECRET' must be an environment variable"

    default_credential = DefaultAzureCredential()

    service_client = DataLakeServiceClient(
        account_url = f"https://{storage_account}.dfs.core.windows.net",
        credential = default_credential,
    )

    file_system_client = service_client.get_file_system_client(file_system=container)
    directory_client = file_system_client.get_directory_client(folder_path)

    try:

        print(f"Deleting folder {folder_path} inside container {container}...")
        directory_client.delete_directory()
        print(f"Folder {folder_path} inside container {container} deleted.")

    except ResourceNotFoundError as e:
        print(f"Folder {folder_path} inside container {container} does not exist.")
