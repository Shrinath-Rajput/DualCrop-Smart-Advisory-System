"""
Test Flask API predictions for Brinjal and Grapes images
"""

import requests
import json
import os
from pathlib import Path

# Test image paths
TEST_IMAGES = {
    "Brinjal Healthy": "artifacts/test/brinjal_Healthy Leaf/healthyleaf_aug0001.jpg",
    "Grapes Healthy": "artifacts/test/Grapes_Grape___healthy/00e00912-bf75-4cf8-8b7d-ad64b73bea5f___Mt.N.V_HL 6067.JPG",
    "Grapes Black Rot": "artifacts/test/Grapes_Grape___Black_rot/00090b0f-c140-4e77-8d20-d39f67b75fcc___FAM_B.Rot 0376.JPG",
    "Grapes Esca": "artifacts/test/Grapes_Grape___Esca_(Black_Measles)/0075b632-2e34-4e4f-9697-fe2b332b7ef8___FAM_B.Msls 4399.JPG",
    "Grapes Leaf Blight": "artifacts/test/Grapes_Grape___Leaf_blight_(Isariopsis_Leaf_Spot)/0001aa74-bbd7-433b-a900-1dccab39d521___FAM_L.Blight 4508.JPG"
}

FLASK_API_URL = "http://localhost:5000/api/predict"

def test_prediction(image_name, image_path):
    """Test prediction on a single image"""
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    try:
        print(f"\n🔄 Testing: {image_name}")
        print(f"   Image: {image_path}")
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(FLASK_API_URL, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"   Prediction: {result.get('prediction', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 0):.2f}%")
            return result
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None


def main():
    print("=" * 70)
    print("🌾 DualCrop Smart Advisory System - Prediction Tests")
    print("=" * 70)
    print(f"🔗 Flask API URL: {FLASK_API_URL}")
    
    results = {}
    
    for image_name, image_path in TEST_IMAGES.items():
        result = test_prediction(image_name, image_path)
        results[image_name] = result
    
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    success_count = sum(1 for r in results.values() if r is not None)
    total_count = len(results)
    
    print(f"\n✅ Successful: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}")
    
    print("\n📈 Results by Category:")
    for image_name, result in results.items():
        if result:
            print(f"  • {image_name}: {result.get('prediction')} ({result.get('confidence', 0):.1f}%)")
        else:
            print(f"  • {image_name}: ❌ FAILED")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
