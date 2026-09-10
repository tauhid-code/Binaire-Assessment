from huggingface_hub import HfApi
from getpass import getpass

token = getpass("Enter your Hugging Face token: ")

try:
    api = HfApi(token=token)
    user = api.whoami()

    print("\nAuthentication successful!")
    print("Username:", user["name"])

except Exception as e:
    print("\nAuthentication failed.")
    print("Error type:", type(e).__name__)
    print("Error:", e)

    if hasattr(e, "response") and e.response is not None:
        print("Status code:", e.response.status_code)
        print("Response:", e.response.text)