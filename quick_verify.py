"""
Quick verification script - Shows disease database and system status
No model loading required
"""

import json
import os
import sys
from pathlib import Path

def quick_verify():
    """Quick system verification"""
    
    print("\n" + "="*80)
    print("DUALCROP DISEASE PREDICTION SYSTEM - VERIFICATION")
    print("="*80)
    
    # Check files exist
    files_to_check = [
        'artifacts/class_names.json',
        'disease_database.json',
        'predict.py',
        'app.py',
        'artifacts/crop_disease_model.h5'
    ]
    
    print("\n📋 SYSTEM FILES STATUS:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) if os.path.isfile(file_path) else 'DIR'
            print(f"  ✓ {file_path:<40} ({size} bytes)" if isinstance(size, int) else f"  ✓ {file_path:<40}")
        else:
            print(f"  ✗ {file_path:<40} NOT FOUND")
    
    # Load and display classes
    print("\n🏷️  MODEL CLASSES:")
    try:
        with open('artifacts/class_names.json') as f:
            class_data = json.load(f)
        
        classes = [class_data[str(i)] for i in range(len(class_data))]
        for i, cls in enumerate(classes):
            print(f"  [{i}] {cls}")
    except Exception as e:
        print(f"  ✗ Error loading classes: {e}")
        return False
    
    # Load disease database
    print("\n🦠 DISEASE DATABASE:")
    try:
        with open('disease_database.json') as f:
            db = json.load(f)
        
        diseases = db.get('diseases', {})
        print(f"  Total disease entries: {len(diseases)}")
        
        print("\n  BRINJAL DISEASES:")
        for cls_name, info in diseases.items():
            if 'Binjal' in cls_name:
                print(f"    • {cls_name}")
                print(f"      Disease: {info.get('disease_name', 'N/A')}")
                print(f"      Status: {info.get('status', 'N/A')}")
                print(f"      Severity: {info.get('severity', 'N/A')}")
        
        print("\n  GRAPES DISEASES:")
        for cls_name, info in diseases.items():
            if 'Grapes' in cls_name:
                print(f"    • {cls_name}")
                print(f"      Disease: {info.get('disease_name', 'N/A')}")
                print(f"      Status: {info.get('status', 'N/A')}")
                print(f"      Severity: {info.get('severity', 'N/A')}")
    
    except Exception as e:
        print(f"  ✗ Error loading disease database: {e}")
        return False
    
    # Show sample prediction data
    print("\n" + "-"*80)
    print("📊 SAMPLE DISEASE INFORMATION")
    print("-"*80)
    
    try:
        # Show Brinjal example
        brinjal_key = None
        for key in diseases.keys():
            if 'Binjal' in key:
                brinjal_key = key
                break
        
        if brinjal_key:
            info = diseases[brinjal_key]
            print(f"\n🌱 BRINJAL - {brinjal_key}")
            print(f"   Disease: {info.get('disease_name', 'N/A')}")
            print(f"   Severity: {info.get('severity', 'N/A')}")
            print(f"   Status: {info.get('status', 'N/A')}")
            print(f"   Confidence Range: {info.get('confidence_range', 'N/A')}")
            
            symptoms = info.get('symptoms', [])
            if symptoms:
                print(f"   Symptoms ({len(symptoms)}):")
                for sym in symptoms[:3]:
                    print(f"     • {sym}")
                if len(symptoms) > 3:
                    print(f"     ... and {len(symptoms)-3} more")
            
            medicines = info.get('recommended_medicines', [])
            if medicines:
                print(f"   Medicines ({len(medicines)}):")
                for med in medicines[:2]:
                    print(f"     • {med.get('name', 'N/A')}")
                    print(f"       Usage: {med.get('usage', 'N/A')}")
                if len(medicines) > 2:
                    print(f"     ... and {len(medicines)-2} more")
            
            if info.get('farmer_advice'):
                print(f"   Farmer Advice:")
                print(f"     {info['farmer_advice'][:100]}...")
        
        # Show Grapes example
        grapes_healthy = None
        for key in diseases.keys():
            if 'Grapes' in key and 'Healthy' in key:
                grapes_healthy = key
                break
        
        if grapes_healthy:
            info = diseases[grapes_healthy]
            print(f"\n🍇 GRAPES - {grapes_healthy}")
            print(f"   Disease: {info.get('disease_name', 'N/A')}")
            print(f"   Severity: {info.get('severity', 'N/A')}")
            print(f"   Status: {info.get('status', 'N/A')}")
            print(f"   Message: {info.get('message', 'N/A')}")
        
        # Show diseased grapes
        grapes_diseased = None
        for key in diseases.keys():
            if 'Grapes' in key and 'Black Rot' in key:
                grapes_diseased = key
                break
        
        if grapes_diseased:
            info = diseases[grapes_diseased]
            print(f"\n🍇 GRAPES (DISEASED) - {grapes_diseased}")
            print(f"   Disease: {info.get('disease_name', 'N/A')}")
            print(f"   Severity: {info.get('severity', 'N/A')}")
            print(f"   Status: {info.get('status', 'N/A')}")
            
            symptoms = info.get('symptoms', [])
            if symptoms:
                print(f"   Symptoms:")
                for sym in symptoms[:3]:
                    print(f"     • {sym}")
    
    except Exception as e:
        print(f"  ✗ Error displaying sample data: {e}")
        return False
    
    # Check dataset
    print("\n" + "-"*80)
    print("📸 DATASET STATUS")
    print("-"*80)
    
    for dataset_type in ['train', 'test']:
        dataset_path = f'artifacts/{dataset_type}'
        if os.path.exists(dataset_path):
            print(f"\n{dataset_type.upper()} Dataset:")
            total = 0
            for class_name in classes:
                class_path = os.path.join(dataset_path, class_name)
                if os.path.exists(class_path):
                    images = [f for f in os.listdir(class_path) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
                    total += len(images)
                    print(f"  {class_name:<50} {len(images):>4} images")
            print(f"  {'TOTAL':<50} {total:>4} images")
    
    # Summary
    print("\n" + "="*80)
    print("✅ SYSTEM VERIFICATION COMPLETE")
    print("="*80)
    print("\nThe disease prediction system is ready!")
    print("\nTo test with an image:")
    print("  python test_disease_prediction.py --single <path_to_image>")
    print("\nTo run the web application:")
    print("  python app.py")
    print("\nTo test dataset samples:")
    print("  python test_disease_prediction.py --samples 1 --dataset test --verbose")
    print("\n" + "="*80 + "\n")
    
    return True


if __name__ == "__main__":
    success = quick_verify()
    sys.exit(0 if success else 1)
