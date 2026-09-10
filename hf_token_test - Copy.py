from huggingface_hub import HfApi
from getpass import getpass

token = getpass("Enter your Hugging Face token: ")

# Clean accidental spaces/newlines from copy-paste
token = token.strip()

print("\nToken diagnostics:")
print("Starts with hf_:", token.startswith("hf_"))
print("Token length:", len(token))
print("Contains spaces:", " " in token)
print("Contains newline:", "\n" in token)

try:
    api = HfApi(token=token)

    model = api.model_info("openbmb/MiniCPM5-2B")

    print("\nSUCCESS!")
    print("Token is accepted by Hugging Face.")
    print("Model:", model.id)

except Exception as e:
    print("\nFAILED")
    print("Error type:", type(e).__name__)
    print("Error:", e)