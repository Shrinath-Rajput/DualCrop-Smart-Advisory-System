"""
Model Testing and Evaluation Module
Tests trained Crop Disease Prediction Model
"""

import os
import json
import numpy as np
import cv2
import random
import matplotlib.pyplot as plt
from predict import CropDiseasePredictorPro
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTester:
    """Test and evaluate the trained model"""
    
    def __init__(self, test_dataset_path="artifacts/test",
                 model_path="crop_disease_model.h5",
                 class_names_path="class_names.json",
                 disease_db_path="disease_database.json"):
        """Initialize tester"""
        self.test_dataset_path = test_dataset_path
        self.predictor = CropDiseasePredictorPro(
            model_path,
            class_names_path,
            disease_db_path
        )
        self.test_results = []
    
    def get_test_images(self):
        """Get all test images organized by class"""
        test_images = {}
        
        if not os.path.exists(self.test_dataset_path):
            logger.warning(f"Test dataset not found: {self.test_dataset_path}")
            return {}
        
        for class_name in os.listdir(self.test_dataset_path):
            class_path = os.path.join(self.test_dataset_path, class_name)
            
            if not os.path.isdir(class_path):
                continue
            
            images = [os.path.join(class_path, img) 
                     for img in os.listdir(class_path)
                     if img.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
            
            if images:
                test_images[class_name] = images
        
        return test_images
    
    def test_random_images(self, num_images=8):
        """Test model on random images"""
        test_images = self.get_test_images()
        
        logger.info("\n" + "="*70)
        logger.info("RANDOM IMAGE TESTING")
        logger.info("="*70)
        logger.info(f"Total test classes: {len(test_images)}")
        
        total_available = sum(len(imgs) for imgs in test_images.values())
        logger.info(f"Total test images available: {total_available}\n")
        
        # Select random images
        selected_images = []
        for class_name, images in test_images.items():
            selected = random.sample(images, min(1, len(images)))
            selected_images.extend([(img, class_name) for img in selected])
        
        if len(selected_images) < num_images:
            remaining = num_images - len(selected_images)
            all_images = []
            for images in test_images.values():
                all_images.extend(images)
            
            additional = random.sample(all_images, min(remaining, len(all_images)))
            selected_images.extend([(img, None) for img in additional])
        
        # Test selected images
        results = []
        for i, (image_path, true_class) in enumerate(selected_images[:num_images], 1):
            try:
                result = self.predictor.predict(image_path)
                result['true_class'] = true_class
                result['image_path'] = image_path
                results.append(result)
                
                match = "✓" if result['predicted_class'] == true_class else "✗"
                logger.info(f"\n[{i}/{num_images}] {os.path.basename(image_path)}")
                logger.info(f"  {match} True: {true_class}")
                logger.info(f"  {match} Predicted: {result['predicted_class']}")
                logger.info(f"  Crop: {result['crop']}")
                logger.info(f"  Status: {result['status']}")
                logger.info(f"  Disease: {result['disease']}")
                logger.info(f"  Confidence: {result['confidence']}")
                
            except Exception as e:
                logger.error(f"\n✗ Error testing {image_path}: {str(e)}")
        
        logger.info("\n" + "="*70)
        return results
    
    def evaluate_on_test_set(self):
        """Evaluate on full test set"""
        test_images = self.get_test_images()
        
        logger.info("\n" + "="*70)
        logger.info("FULL TEST SET EVALUATION")
        logger.info("="*70)
        
        total_correct = 0
        total_images = 0
        class_results = {}
        
        for class_name, images in sorted(test_images.items()):
            correct = 0
            logger.info(f"\nTesting {class_name}...")
            
            for image_path in images:
                try:
                    result = self.predictor.predict(image_path)
                    total_images += 1
                    
                    if result['predicted_class'] == class_name:
                        correct += 1
                        total_correct += 1
                
                except Exception as e:
                    total_images += 1
                    logger.warning(f"Error: {str(e)}")
            
            accuracy = (correct / len(images) * 100) if images else 0
            class_results[class_name] = {
                'correct': correct,
                'total': len(images),
                'accuracy': accuracy
            }
            
            logger.info(f"  {correct}/{len(images)} ({accuracy:.2f}%)")
        
        overall_accuracy = (total_correct / total_images * 100) if total_images > 0 else 0
        
        logger.info("\n" + "-"*70)
        logger.info(f"Overall Accuracy: {total_correct}/{total_images} ({overall_accuracy:.2f}%)")
        logger.info("="*70 + "\n")
        
        return class_results, overall_accuracy
    
    def visualize_predictions(self, results, num_display=8):
        """Visualize predictions with images"""
        num_display = min(num_display, len(results))
        
        logger.info(f"Generating visualization for {num_display} predictions...")
        
        grid_size = int(np.ceil(np.sqrt(num_display)))
        fig, axes = plt.subplots(grid_size, grid_size, figsize=(15, 15))
        axes = axes.flatten()
        
        for idx, (ax, result) in enumerate(zip(axes, results[:num_display])):
            try:
                image = cv2.imread(result['image_path'])
                if image is not None:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    ax.imshow(image)
                
                match = "✓" if result['predicted_class'] == result.get('true_class') else "✗"
                title = f"{match} {result['predicted_class']}\n{result['confidence']}"
                if result.get('true_class'):
                    title = f"{match} Pred: {result['predicted_class']}\nTrue: {result.get('true_class')}\n{result['confidence']}"
                
                ax.set_title(title, fontsize=10, fontweight='bold')
                ax.axis('off')
                
            except Exception as e:
                ax.text(0.5, 0.5, f"Error: {str(e)}", 
                       ha='center', va='center', transform=ax.transAxes)
                ax.axis('off')
        
        for idx in range(num_display, len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        plt.savefig('test_predictions_visualization.png', dpi=300, bbox_inches='tight')
        logger.info("✓ Visualization saved to test_predictions_visualization.png")
        plt.close()
    
    def generate_test_report(self, results, class_results, overall_accuracy):
        """Generate comprehensive test report"""
        report = {
            'overall_accuracy': overall_accuracy,
            'total_tests': len(results),
            'class_results': class_results,
            'predictions': []
        }
        
        for result in results:
            entry = {
                'image': result['image_path'],
                'true_class': result.get('true_class'),
                'predicted_class': result['predicted_class'],
                'confidence': result['confidence'],
                'crop': result['crop'],
                'status': result['status'],
                'disease': result['disease'],
                'correct': result['predicted_class'] == result.get('true_class')
            }
            report['predictions'].append(entry)
        
        report_path = 'test_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✓ Test report saved to {report_path}")
        return report


def run_comprehensive_test():
    """Run comprehensive model testing"""
    
    logger.info("\n" + "█"*70)
    logger.info("█" + "CROP DISEASE MODEL - TESTING & EVALUATION".center(68) + "█")
    logger.info("█"*70)
    
    try:
        tester = ModelTester()
        
        logger.info("\n[STEP 1/4] Testing on random images...")
        random_results = tester.test_random_images(num_images=8)
        
        logger.info("\n[STEP 2/4] Evaluating on full test set...")
        class_results, overall_accuracy = tester.evaluate_on_test_set()
        
        logger.info("\n[STEP 3/4] Visualizing predictions...")
        tester.visualize_predictions(random_results, num_display=8)
        
        logger.info("\n[STEP 4/4] Generating test report...")
        report = tester.generate_test_report(random_results, class_results, overall_accuracy)
        
        logger.info("\n" + "="*70)
        logger.info("TEST SUMMARY")
        logger.info("="*70)
        logger.info(f"✓ Model: crop_disease_model.h5")
        logger.info(f"✓ Overall Test Accuracy: {overall_accuracy:.2f}%")
        logger.info(f"✓ Random Tests Completed: {len(random_results)}")
        logger.info(f"✓ Test Report Saved: test_report.json")
        logger.info(f"✓ Visualization Saved: test_predictions_visualization.png")
        logger.info("="*70 + "\n")
        
        logger.info("✅ Testing completed successfully!\n")
        
    except Exception as e:
        logger.error(f"\n❌ ERROR: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    run_comprehensive_test()
