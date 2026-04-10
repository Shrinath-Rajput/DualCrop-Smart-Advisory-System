"""
Test script for PredictPipeline
Tests model predictions on sample images
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline.predict_pipeline import PredictPipeline
from src.logger import logging
from src.exception import CustomException


class TestPredictPipeline:
    """Test suite for PredictPipeline"""
    
    def __init__(self):
        self.pipeline = None
        self.result_log = []
    
    def setup(self):
        """Initialize the pipeline"""
        try:
            logging.info("=" * 60)
            logging.info("SETTING UP PREDICT PIPELINE TEST")
            logging.info("=" * 60)
            
            self.pipeline = PredictPipeline()
            
            logging.info(f"✅ Pipeline initialized")
            logging.info(f"📁 Model path: {self.pipeline.model_path}")
            logging.info(f"📊 Classes detected: {len(self.pipeline.class_names)}")
            logging.info(f"🏷️  Class names: {self.pipeline.class_names}")
            logging.info("=" * 60)
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Setup failed: {str(e)}")
            raise CustomException(e, sys)
    
    def test_single_image(self, image_path):
        """Test prediction on a single image"""
        try:
            if not os.path.exists(image_path):
                logging.warning(f"⚠️  Image not found: {image_path}")
                return None
            
            logging.info(f"\n📸 Testing image: {image_path}")
            
            predicted_class, confidence = self.pipeline.predict(image_path)
            
            result = {
                'image': image_path,
                'predicted_class': predicted_class,
                'confidence': confidence,
                'status': '✅ SUCCESS'
            }
            
            logging.info(f"   Predicted class: {predicted_class}")
            logging.info(f"   Confidence: {confidence:.2%}")
            logging.info(f"   Status: ✅ SUCCESS")
            
            self.result_log.append(result)
            return result
            
        except Exception as e:
            logging.error(f"❌ Prediction failed for {image_path}: {str(e)}")
            result = {
                'image': image_path,
                'error': str(e),
                'status': '❌ FAILED'
            }
            self.result_log.append(result)
            return result
    
    def test_from_test_directory(self):
        """Test predictions on images from artifacts/test directory"""
        try:
            test_dir = os.path.join("artifacts", "test")
            
            if not os.path.exists(test_dir):
                logging.warning(f"⚠️  Test directory not found: {test_dir}")
                return
            
            logging.info(f"\n{'=' * 60}")
            logging.info(f"TESTING IMAGES FROM: {test_dir}")
            logging.info(f"{'=' * 60}")
            
            class_folders = sorted([d for d in os.listdir(test_dir) 
                                   if os.path.isdir(os.path.join(test_dir, d))])
            
            logging.info(f"Found {len(class_folders)} disease classes\n")
            
            total_tested = 0
            total_correct = 0
            
            for class_folder in class_folders:
                class_path = os.path.join(test_dir, class_folder)
                images = [f for f in os.listdir(class_path) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
                
                if not images:
                    logging.info(f"⚠️  No images in {class_folder}")
                    continue
                
                logging.info(f"📂 Class: {class_folder}")
                logging.info(f"   Images found: {len(images)}")
                
                # Test first 3 images per class
                test_count = min(3, len(images))
                correct_count = 0
                
                for img_file in images[:test_count]:
                    img_path = os.path.join(class_path, img_file)
                    result = self.test_single_image(img_path)
                    
                    if result and 'predicted_class' in result:
                        is_correct = result['predicted_class'] == class_folder
                        if is_correct:
                            correct_count += 1
                        
                        status = "✅" if is_correct else "❌"
                        logging.info(f"   {status} {img_file}: {result['predicted_class']}")
                    
                    total_tested += 1
                
                total_correct += correct_count
                class_accuracy = (correct_count / test_count) * 100
                logging.info(f"   Accuracy for this class: {class_accuracy:.1f}%\n")
            
            if total_tested > 0:
                overall_accuracy = (total_correct / total_tested) * 100
                logging.info(f"{'=' * 60}")
                logging.info(f"📊 OVERALL TEST RESULTS")
                logging.info(f"{'=' * 60}")
                logging.info(f"Total images tested: {total_tested}")
                logging.info(f"Correct predictions: {total_correct}")
                logging.info(f"Overall accuracy: {overall_accuracy:.1f}%")
                logging.info(f"{'=' * 60}\n")
        
        except Exception as e:
            logging.error(f"❌ Test from directory failed: {str(e)}")
            raise CustomException(e, sys)
    
    def test_sample_images(self, sample_images):
        """Test predictions on provided sample images"""
        try:
            logging.info(f"\n{'=' * 60}")
            logging.info(f"TESTING SAMPLE IMAGES")
            logging.info(f"{'=' * 60}\n")
            
            for img_path in sample_images:
                self.test_single_image(img_path)
        
        except Exception as e:
            logging.error(f"❌ Sample image test failed: {str(e)}")
            raise CustomException(e, sys)
    
    def generate_report(self):
        """Generate test report"""
        logging.info(f"\n{'=' * 60}")
        logging.info(f"📋 TEST REPORT SUMMARY")
        logging.info(f"{'=' * 60}")
        
        total_tests = len(self.result_log)
        successful_tests = sum(1 for r in self.result_log if r.get('status') == '✅ SUCCESS')
        failed_tests = total_tests - successful_tests
        
        logging.info(f"Total tests run: {total_tests}")
        logging.info(f"✅ Successful: {successful_tests}")
        logging.info(f"❌ Failed: {failed_tests}")
        
        if successful_tests > 0:
            success_rate = (successful_tests / total_tests) * 100
            logging.info(f"Success rate: {success_rate:.1f}%")
        
        logging.info(f"{'=' * 60}\n")
        
        return {
            'total_tests': total_tests,
            'successful': successful_tests,
            'failed': failed_tests,
            'results': self.result_log
        }


def main():
    """Main test execution"""
    try:
        # Initialize test suite
        test_suite = TestPredictPipeline()
        test_suite.setup()
        
        # Test 1: Images from test directory
        test_suite.test_from_test_directory()
        
        # Test 2: Sample images (if provided)
        sample_images = [
            # Add specific image paths here to test
            # Example:
            # "path/to/test/image.jpg",
        ]
        
        if sample_images:
            test_suite.test_sample_images(sample_images)
        
        # Generate report
        report = test_suite.generate_report()
        
        logging.info("✅ TEST COMPLETED SUCCESSFULLY")
        
        return report
    
    except Exception as e:
        logging.error(f"❌ TEST FAILED: {str(e)}")
        raise


if __name__ == "__main__":
    main()
