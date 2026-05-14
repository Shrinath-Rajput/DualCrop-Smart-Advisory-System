"""
QUICK DISEASE PREDICTION - Fast command line tool for Brinjal and Grapes
Usage: python quick_predict.py <image_path>
"""

import os
import sys
import json
import warnings

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

def quick_predict(image_path):
    """Quick disease prediction for any image"""
    
    if not os.path.exists(image_path):
        print(f"❌ IMAGE NOT FOUND: {image_path}")
        return False
    
    try:
        # Import here to avoid loading if not needed
        from predict import CropDiseasePredictorPro
        
        print(f"\n🔄 Loading prediction model...")
        predictor = CropDiseasePredictorPro()
        
        print(f"📸 Analyzing image: {os.path.basename(image_path)}")
        result = predictor.predict(image_path)
        
        if not result.get('success', False):
            print(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Display results
        print_disease_result(result)
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def print_disease_result(result):
    """Print disease prediction results in user-friendly format"""
    
    crop = result.get('crop', 'Unknown')
    disease = result.get('disease', 'Unknown')
    status = result.get('status', 'Unknown')
    severity = result.get('severity', 'Unknown')
    confidence = result.get('confidence', 'N/A')
    
    print("\n" + "="*80)
    print(f"🌾 CROP: {crop}")
    print("="*80)
    
    # Disease status
    if status == 'Healthy':
        print(f"\n✅ STATUS: HEALTHY")
        print(f"   {result.get('message', 'Plant is in good condition')}")
    else:
        print(f"\n🔴 STATUS: {status.upper()}")
        print(f"   Disease: {disease}")
        print(f"   Severity: {severity}")
        print(f"   Confidence: {confidence}")
        
        # Symptoms
        if result.get('symptoms'):
            print(f"\n📋 SYMPTOMS OBSERVED:")
            for symptom in result['symptoms'][:5]:
                print(f"   • {symptom}")
        
        # Treatment
        if result.get('recommended_medicines'):
            print(f"\n💊 TREATMENT:")
            for i, med in enumerate(result['recommended_medicines'][:3], 1):
                print(f"   {i}. {med.get('name', 'N/A')}")
                print(f"      • Quantity: {med.get('quantity', 'N/A')}")
                print(f"      • Usage: {med.get('usage', 'N/A')}")
        
        # Organic solutions
        if result.get('organic_solutions'):
            print(f"\n🌿 ORGANIC ALTERNATIVES:")
            for solution in result['organic_solutions'][:3]:
                print(f"   • {solution}")
        
        # Prevention
        if result.get('prevention_tips'):
            print(f"\n🛡️  PREVENTION TIPS:")
            for tip in result['prevention_tips'][:3]:
                print(f"   • {tip}")
        
        # Farmer advice
        if result.get('farmer_advice'):
            print(f"\n👨‍🌾 FARMER ADVICE:")
            print(f"   {result['farmer_advice']}")
    
    print("\n" + "="*80 + "\n")


def show_examples():
    """Show example images available"""
    print("\n📸 AVAILABLE TEST IMAGES:")
    print("="*80)
    
    test_path = 'artifacts/test'
    if os.path.exists(test_path):
        for class_name in sorted(os.listdir(test_path)):
            class_path = os.path.join(test_path, class_name)
            if os.path.isdir(class_path):
                images = [f for f in os.listdir(class_path)
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if images:
                    example = os.path.join(class_path, images[0])
                    print(f"  {class_name}")
                    print(f"    Example: {example}")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick Disease Prediction for Brinjal and Grapes')
    parser.add_argument('image', nargs='?', help='Path to plant leaf image')
    parser.add_argument('--examples', action='store_true', help='Show available test images')
    
    args = parser.parse_args()
    
    if args.examples:
        show_examples()
    elif args.image:
        quick_predict(args.image)
    else:
        print("\n🌾 DUALCROP QUICK DISEASE PREDICTION")
        print("="*80)
        print("\nUsage:")
        print("  python quick_predict.py <image_path>")
        print("\nExamples:")
        print("  python quick_predict.py path/to/brinjal_leaf.jpg")
        print("  python quick_predict.py path/to/grape_leaf.jpg")
        print("\nShow available test images:")
        print("  python quick_predict.py --examples")
        print("\n" + "="*80 + "\n")
