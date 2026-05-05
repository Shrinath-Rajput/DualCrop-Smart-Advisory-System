#!/usr/bin/env python3
import requests
import os

# Test image path
test_image = r"artifacts\test\brinjal_Healthy Leaf\healthyleaf_aug0001.jpg"

if not os.path.exists(test_image):
    print(f"❌ Test image not found: {test_image}")
    exit(1)

print(f"📸 Testing Flask API with image: {test_image}")

# Open the image and send to Flask
try:
    with open(test_image, "rb") as f:
        files = {"file": f}
        response = requests.post("http://localhost:5000/api/predict", files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
