import os
import requests

from dotenv import load_dotenv
from huggingface_hub import HfApi, snapshot_download



load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in .env file")



api = HfApi(token=HF_TOKEN)

print("=" * 60)
print("HUGGING FACE TASK 1")
print("=" * 60)



user = api.whoami()

print("\nAuthentication successful!")
print("Username:", user["name"])



print("\nFollow step:")
print("Hugging Face follow endpoint requires web-session authentication.")
print("Skipping automated follow API call for now.")



MODEL_1 = "freznelai/FreznelAI_1.0_Face-Landmarker_500M_FZFP4_FRZm"

print("\n" + "=" * 60)
print("Downloading Model 1")
print("=" * 60)

model1_path = snapshot_download(
    repo_id=MODEL_1,
    token=HF_TOKEN,
    local_dir="./models/face_landmarker"
)

print("\nModel 1 downloaded to:")
print(model1_path)




MODEL_2 = "freznelai/FreznelAI_1.0_Face-Detector_500M_FZFP4_FRZm"

print("\n" + "=" * 60)
print("Downloading Model 2")
print("=" * 60)

model2_path = snapshot_download(
    repo_id=MODEL_2,
    token=HF_TOKEN,
    local_dir="./models/face_detector"
)

print("\nModel 2 downloaded to:")
print(model2_path)




print("\n" + "=" * 60)
print("TASK 1 COMPLETED")
print("=" * 60)