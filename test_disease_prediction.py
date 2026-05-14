"""
Comprehensive Disease Prediction Testing Script
Tests the prediction system with actual images from dataset
"""

import os
import json
import sys
import random
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from predict import CropDiseasePredictorPro, print_result


def get_sample_images_from_dataset(dataset_type='train', samples_per_class=1):
    """Get sample images from dataset"""
    samples = {}
    dataset_path = os.path.join('artifacts', dataset_type)
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset path not found: {dataset_path}")
        return samples
    
    # Get all class directories
    classes = [d for d in os.listdir(dataset_path) 
               if os.path.isdir(os.path.join(dataset_path, d))]
    
    for class_name in sorted(classes):
        class_path = os.path.join(dataset_path, class_name)
        images = [f for f in os.listdir(class_path)
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
        
        if images:
            # Randomly select samples
            selected = random.sample(images, min(samples_per_class, len(images)))
            samples[class_name] = [os.path.join(class_path, img) for img in selected]
            print(f"✓ Found {len(selected)} sample(s) from class: {class_name}")
    
    return samples


def test_predictions(samples, verbose=True):
    """Test predictions on sample images"""
    print("\n" + "="*80)
    print("DISEASE PREDICTION TESTING SYSTEM")
    print("="*80)
    
    try:
        predictor = CropDiseasePredictorPro()
        print(f"\n✓ Predictor initialized")
        print(f"  Classes: {predictor.classes}")
        print(f"  Disease database entries: {len(predictor.disease_database)}")
    except Exception as e:
        print(f"❌ Failed to initialize predictor: {e}")
        return False
    
    # Test predictions
    results = {
        'total': 0,
        'correct': 0,
        'predictions': []
    }
    
    for class_name, image_paths in samples.items():
        print(f"\n" + "-"*80)
        print(f"Testing class: {class_name}")
        print("-"*80)
        
        for image_path in image_paths:
            results['total'] += 1
            
            try:
                print(f"\n📷 Image: {os.path.basename(image_path)}")
                
                # Make prediction
                result = predictor.predict(image_path)
                
                if not result.get('success', False):
                    print(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
                    continue
                
                # Extract results
                predicted_class = result['predicted_class']
                confidence = float(result['confidence_score'])
                disease = result['disease']
                status = result['status']
                severity = result['severity']
                crop = result['crop']
                
                # Check if prediction is correct
                is_correct = predicted_class == class_name
                if is_correct:
                    results['correct'] += 1
                    mark = "✓"
                else:
                    mark = "✗"
                
                # Print prediction details
                print(f"  {mark} Predicted: {predicted_class}")
                print(f"    Disease: {disease}")
                print(f"    Crop: {crop}")
                print(f"    Status: {status}")
                print(f"    Severity: {severity}")
                print(f"    Confidence: {confidence*100:.2f}%")
                
                # Show symptoms if diseased
                if status == 'Diseased' and result.get('symptoms'):
                    print(f"    Symptoms: {', '.join(result['symptoms'][:2])}...")
                
                # Store result
                results['predictions'].append({
                    'image': os.path.basename(image_path),
                    'true_class': class_name,
                    'predicted_class': predicted_class,
                    'is_correct': is_correct,
                    'confidence': confidence,
                    'disease': disease,
                    'crop': crop,
                    'status': status
                })
                
                if verbose and not is_correct:
                    print(f"\n⚠️  MISPREDICTION DETAILS:")
                    print(f"    Expected: {class_name}")
                    print(f"    Got: {predicted_class}")
                    print(f"    Confidence: {confidence*100:.2f}%")
                    
                    # Show top 3 predictions
                    if result.get('all_predictions'):
                        print(f"    Top predictions:")
                        for pred in result['all_predictions'][:3]:
                            print(f"      - {pred['class']}: {pred['confidence']}")
            
            except Exception as e:
                print(f"❌ Error testing image: {str(e)}")
                import traceback
                traceback.print_exc()
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if results['total'] > 0:
        accuracy = (results['correct'] / results['total']) * 100
        print(f"Total predictions: {results['total']}")
        print(f"Correct predictions: {results['correct']}")
        print(f"Accuracy: {accuracy:.2f}%")
        
        # Print per-class accuracy
        print(f"\nPer-class accuracy:")
        class_stats = {}
        for pred in results['predictions']:
            true_class = pred['true_class']
            if true_class not in class_stats:
                class_stats[true_class] = {'total': 0, 'correct': 0}
            
            class_stats[true_class]['total'] += 1
            if pred['is_correct']:
                class_stats[true_class]['correct'] += 1
        
        for class_name in sorted(class_stats.keys()):
            stats = class_stats[class_name]
            class_accuracy = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
            print(f"  {class_name}: {stats['correct']}/{stats['total']} ({class_accuracy:.2f}%)")
    
    print("="*80 + "\n")
    
    return results


def test_single_image(image_path):
    """Test prediction on a single image"""
    print("\n" + "="*80)
    print("SINGLE IMAGE PREDICTION TEST")
    print("="*80)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    try:
        predictor = CropDiseasePredictorPro()
        print(f"✓ Predictor initialized\n")
        
        print(f"📷 Testing image: {image_path}")
        result = predictor.predict(image_path)
        
        if result.get('success'):
            print_result(result)
        else:
            print(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


def generate_test_report(results, output_file='prediction_test_report.json'):
    """Generate test report"""
    report = {
        'summary': {
            'total_predictions': results['total'],
            'correct_predictions': results['correct'],
            'accuracy': (results['correct'] / results['total'] * 100) if results['total'] > 0 else 0
        },
        'predictions': results['predictions']
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✓ Report saved: {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test disease prediction system')
    parser.add_argument('--single', type=str, help='Test a single image')
    parser.add_argument('--samples', type=int, default=2, help='Number of samples per class')
    parser.add_argument('--dataset', choices=['train', 'test'], default='test', help='Dataset to use')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--report', action='store_true', help='Generate JSON report')
    
    args = parser.parse_args()
    
    if args.single:
        # Test single image
        test_single_image(args.single)
    else:
        # Test multiple images from dataset
        print(f"\nLoading sample images from {args.dataset} dataset...")
        samples = get_sample_images_from_dataset(dataset_type=args.dataset, 
                                                 samples_per_class=args.samples)
        
        if samples:
            results = test_predictions(samples, verbose=args.verbose)
            
            if args.report:
                generate_test_report(results)
        else:
            print("❌ No sample images found")
