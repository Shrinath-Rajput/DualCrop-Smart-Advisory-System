"""
Validation script to check class name mapping and disease database
Does NOT require TensorFlow or heavy dependencies
"""

import os
import json
import sys

def validate_class_disease_mapping():
    """Validate that all classes have matching disease database entries"""
    
    print("="*80)
    print("CLASS AND DISEASE DATABASE VALIDATION")
    print("="*80)
    
    # Load class names
    class_names_path = 'artifacts/class_names.json'
    if not os.path.exists(class_names_path):
        print(f"❌ Class names file not found: {class_names_path}")
        return False
    
    with open(class_names_path) as f:
        class_names_data = json.load(f)
    
    # Extract classes - handle both formats
    if 'classes' in class_names_data:
        classes = [class_names_data['classes'][str(i)] for i in range(len(class_names_data['classes']))]
    else:
        # Direct mapping format
        classes = [class_names_data[str(i)] for i in range(len(class_names_data))]
    
    print(f"\n✓ Found {len(classes)} classes:")
    for i, cls in enumerate(classes):
        print(f"  [{i}] {cls}")
    
    # Load disease database
    disease_db_path = 'disease_database.json'
    if not os.path.exists(disease_db_path):
        print(f"❌ Disease database file not found: {disease_db_path}")
        return False
    
    with open(disease_db_path) as f:
        disease_db = json.load(f)
    
    disease_keys = list(disease_db['diseases'].keys())
    print(f"\n✓ Found {len(disease_keys)} disease entries in database:")
    for key in disease_keys:
        print(f"  • {key}")
    
    # Check mapping
    print("\n" + "-"*80)
    print("CLASS TO DISEASE MAPPING VALIDATION")
    print("-"*80)
    
    all_valid = True
    
    for class_name in classes:
        disease_info = disease_db['diseases'].get(class_name)
        
        if disease_info:
            print(f"\n✓ {class_name}")
            print(f"  └─ Crop: {disease_info.get('crop', 'N/A')}")
            print(f"  └─ Disease: {disease_info.get('disease_name', 'N/A')}")
            print(f"  └─ Status: {disease_info.get('status', 'N/A')}")
            print(f"  └─ Severity: {disease_info.get('severity', 'N/A')}")
            print(f"  └─ Symptoms: {len(disease_info.get('symptoms', []))} listed")
            print(f"  └─ Medicines: {len(disease_info.get('recommended_medicines', []))} listed")
        else:
            print(f"\n❌ {class_name}")
            print(f"  └─ NO DISEASE DATABASE ENTRY FOUND!")
            all_valid = False
    
    # Check for unused database entries
    print("\n" + "-"*80)
    print("UNUSED DATABASE ENTRIES")
    print("-"*80)
    
    unused = [key for key in disease_keys if key not in classes]
    
    if unused:
        print(f"\n⚠️  {len(unused)} unused entries in disease database:")
        for key in unused:
            print(f"  • {key}")
    else:
        print(f"\n✓ All disease database entries are used")
    
    # Validate directory structure
    print("\n" + "-"*80)
    print("DATASET DIRECTORY STRUCTURE VALIDATION")
    print("-"*80)
    
    for dataset_type in ['train', 'test']:
        dataset_path = f'artifacts/{dataset_type}'
        if os.path.exists(dataset_path):
            dirs = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
            print(f"\n✓ {dataset_path}:")
            
            for dir_name in sorted(dirs):
                dir_path = os.path.join(dataset_path, dir_name)
                images = [f for f in os.listdir(dir_path) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
                
                # Check if directory name matches a class
                matches_class = dir_name in classes
                match_status = "✓" if matches_class else "✗"
                
                print(f"  {match_status} {dir_name} ({len(images)} images)")
                
                if not matches_class:
                    all_valid = False
    
    # Summary
    print("\n" + "="*80)
    if all_valid:
        print("✓ VALIDATION PASSED - All classes and disease entries are properly mapped!")
    else:
        print("❌ VALIDATION FAILED - There are mapping issues that need to be fixed!")
    print("="*80 + "\n")
    
    return all_valid


def print_sample_disease_info():
    """Print sample disease information for all classes"""
    
    print("\n" + "="*80)
    print("SAMPLE DISEASE INFORMATION BY CLASS")
    print("="*80)
    
    with open('disease_database.json') as f:
        disease_db = json.load(f)
    
    for class_name, disease_info in disease_db['diseases'].items():
        print(f"\n{'='*80}")
        print(f"CLASS: {class_name}")
        print(f"{'='*80}")
        print(f"Crop: {disease_info.get('crop', 'N/A')}")
        print(f"Disease: {disease_info.get('disease_name', 'N/A')}")
        print(f"Status: {disease_info.get('status', 'N/A')}")
        print(f"Severity: {disease_info.get('severity', 'N/A')}")
        print(f"Confidence Range: {disease_info.get('confidence_range', 'N/A')}")
        
        if disease_info.get('symptoms'):
            print(f"\nSymptoms:")
            for symptom in disease_info['symptoms'][:3]:
                print(f"  • {symptom}")
            if len(disease_info['symptoms']) > 3:
                print(f"  ... and {len(disease_info['symptoms']) - 3} more")
        
        if disease_info.get('recommended_medicines'):
            print(f"\nRecommended Medicines:")
            for med in disease_info['recommended_medicines'][:2]:
                print(f"  • {med.get('name', 'N/A')}")
                print(f"    Usage: {med.get('usage', 'N/A')}")
            if len(disease_info['recommended_medicines']) > 2:
                print(f"  ... and {len(disease_info['recommended_medicines']) - 2} more")
        
        if disease_info.get('farmer_advice'):
            print(f"\nFarmer Advice:")
            print(f"  {disease_info['farmer_advice']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate class names and disease database mapping')
    parser.add_argument('--info', action='store_true', help='Print sample disease information')
    
    args = parser.parse_args()
    
    # Run validation
    is_valid = validate_class_disease_mapping()
    
    # Print info if requested
    if args.info:
        print_sample_disease_info()
    
    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)
