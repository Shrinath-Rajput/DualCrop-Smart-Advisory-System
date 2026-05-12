#!/usr/bin/env python3
"""
Crop Disease Prediction System - ML Pipeline Interactive Menu
Cross-platform launcher for training, testing, and predictions
"""

import os
import sys
import subprocess
from pathlib import Path


class MLPipelineMenu:
    """Interactive menu for ML pipeline operations"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.model_path = self.base_path / "crop_disease_model.h5"
        self.class_names_path = self.base_path / "class_names.json"
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print menu header"""
        print("\n" + "="*60)
        print("  CROP DISEASE PREDICTION SYSTEM - ML PIPELINE".center(60))
        print("="*60 + "\n")
    
    def print_menu(self):
        """Print menu options"""
        self.print_header()
        print("1. Install Dependencies")
        print("2. Train Model")
        print("3. Test Model")
        print("4. Predict Single Image")
        print("5. Batch Predict Images")
        print("6. View Model Information")
        print("7. View Training History")
        print("8. Exit")
        print("\n" + "="*60)
    
    def install_dependencies(self):
        """Install required dependencies"""
        self.clear_screen()
        print("\n" + "="*60)
        print("Installing Dependencies".center(60))
        print("="*60 + "\n")
        
        req_file = self.base_path / "requirements_ml.txt"
        if req_file.exists():
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
            print("\n✓ Dependencies installed successfully!")
        else:
            print(f"✗ Error: {req_file} not found!")
        
        input("\nPress Enter to continue...")
    
    def train_model(self):
        """Run model training"""
        self.clear_screen()
        print("\n" + "="*60)
        print("Training Model".center(60))
        print("="*60 + "\n")
        
        train_script = self.base_path / "train_model.py"
        if train_script.exists():
            subprocess.run([sys.executable, str(train_script)])
            print("\n✓ Training completed!")
        else:
            print(f"✗ Error: {train_script} not found!")
        
        input("\nPress Enter to continue...")
    
    def test_model(self):
        """Run model testing"""
        self.clear_screen()
        print("\n" + "="*60)
        print("Testing Model".center(60))
        print("="*60 + "\n")
        
        if not self.model_path.exists():
            print(f"✗ Error: Model not found at {self.model_path}")
            print("  Please train the model first using option 2")
            input("\nPress Enter to continue...")
            return
        
        test_script = self.base_path / "test_model.py"
        if test_script.exists():
            subprocess.run([sys.executable, str(test_script)])
            print("\n✓ Testing completed!")
        else:
            print(f"✗ Error: {test_script} not found!")
        
        input("\nPress Enter to continue...")
    
    def predict_single_image(self):
        """Predict on a single image"""
        self.clear_screen()
        print("\n" + "="*60)
        print("Single Image Prediction".center(60))
        print("="*60 + "\n")
        
        if not self.model_path.exists():
            print(f"✗ Error: Model not found at {self.model_path}")
            print("  Please train the model first using option 2")
            input("\nPress Enter to continue...")
            return
        
        image_path = input("Enter image path: ").strip()
        
        if not Path(image_path).exists():
            print(f"✗ Error: Image not found at {image_path}")
            input("\nPress Enter to continue...")
            return
        
        print("\nMaking prediction...\n")
        
        try:
            from predict import predict_single_image, print_prediction
            result = predict_single_image(image_path)
            print_prediction(result)
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        input("Press Enter to continue...")
    
    def batch_predict(self):
        """Batch predict on multiple images"""
        self.clear_screen()
        print("\n" + "="*60)
        print("Batch Image Prediction".center(60))
        print("="*60 + "\n")
        
        if not self.model_path.exists():
            print(f"✗ Error: Model not found at {self.model_path}")
            print("  Please train the model first using option 2")
            input("\nPress Enter to continue...")
            return
        
        folder_path = input("Enter folder containing images: ").strip()
        
        if not Path(folder_path).exists():
            print(f"✗ Error: Folder not found at {folder_path}")
            input("\nPress Enter to continue...")
            return
        
        # Find all image files
        images = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']:
            images.extend(Path(folder_path).glob(ext))
            images.extend(Path(folder_path).glob(ext.upper()))
        
        if not images:
            print(f"✗ Error: No images found in {folder_path}")
            input("\nPress Enter to continue...")
            return
        
        print(f"\nFound {len(images)} images. Processing...\n")
        
        try:
            from predict import CropDiseasePredictor
            predictor = CropDiseasePredictor()
            
            results = predictor.predict_batch([str(img) for img in images])
            
            print("\n" + "="*60)
            print("BATCH PREDICTION RESULTS".center(60))
            print("="*60)
            
            for result in results:
                if result['status'] == 'success':
                    pred = result['prediction']
                    print(f"\n{Path(result['image']).name}:")
                    print(f"  Crop: {pred['crop']}")
                    print(f"  Status: {pred['status']}")
                    print(f"  Disease: {pred['disease']}")
                    print(f"  Confidence: {pred['confidence']}")
                else:
                    print(f"\n{result['image']}: ✗ Error - {result['error']}")
            
            print("\n" + "="*60)
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        input("\nPress Enter to continue...")
    
    def view_model_info(self):
        """Display model information"""
        self.clear_screen()
        print("\n" + "="*60)
        print("Model Information".center(60))
        print("="*60 + "\n")
        
        if not self.model_path.exists():
            print(f"✗ Error: Model not found at {self.model_path}")
            print("  Please train the model first using option 2")
            input("\nPress Enter to continue...")
            return
        
        try:
            from predict import CropDiseasePredictor
            predictor = CropDiseasePredictor()
            info = predictor.get_model_info()
            
            print(f"Model Path: {info['model_path']}")
            print(f"Number of Classes: {info['num_classes']}")
            print(f"Model Layers: {info['model_layers']}")
            print(f"Input Shape: {info['input_shape']}")
            print(f"Output Shape: {info['output_shape']}\n")
            
            print("Classes:")
            for i, cls in enumerate(info['classes'], 1):
                print(f"  {i}. {cls}")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        input("\nPress Enter to continue...")
    
    def view_training_history(self):
        """Display training history"""
        self.clear_screen()
        print("\n" + "="*60)
        print("Training History".center(60))
        print("="*60 + "\n")
        
        import json
        history_file = self.base_path / "training_history.json"
        
        if not history_file.exists():
            print("✗ Error: Training history not found")
            print("  Please train the model first using option 2")
            input("\nPress Enter to continue...")
            return
        
        try:
            with open(history_file) as f:
                history = json.load(f)
            
            epochs = len(history['accuracy'])
            
            print(f"Total Epochs: {epochs}\n")
            print("Epoch  | Train Acc | Val Acc | Train Loss | Val Loss")
            print("-" * 60)
            
            for i in range(epochs):
                print(f"{i+1:5d}  | {history['accuracy'][i]:9.4f} | {history['val_accuracy'][i]:7.4f} | "
                      f"{history['loss'][i]:10.4f} | {history['val_loss'][i]:8.4f}")
            
            print("\n" + "-" * 60)
            print(f"Final Train Accuracy: {history['accuracy'][-1]:.4f}")
            print(f"Final Val Accuracy: {history['val_accuracy'][-1]:.4f}")
            print(f"Final Train Loss: {history['loss'][-1]:.4f}")
            print(f"Final Val Loss: {history['val_loss'][-1]:.4f}")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Run the interactive menu"""
        while True:
            self.clear_screen()
            self.print_menu()
            
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == "1":
                self.install_dependencies()
            elif choice == "2":
                self.train_model()
            elif choice == "3":
                self.test_model()
            elif choice == "4":
                self.predict_single_image()
            elif choice == "5":
                self.batch_predict()
            elif choice == "6":
                self.view_model_info()
            elif choice == "7":
                self.view_training_history()
            elif choice == "8":
                self.clear_screen()
                print("\nGoodbye! 👋\n")
                break
            else:
                print("✗ Invalid choice! Press Enter to try again...")
                input()


if __name__ == "__main__":
    menu = MLPipelineMenu()
    menu.run()
