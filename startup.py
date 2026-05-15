"""
CROP DISEASE PREDICTION SYSTEM - STARTUP & HELPER SCRIPT
=========================================================

This script provides:
1. Interactive setup wizard
2. Validation of system
3. Quick start options
4. Debugging tools

Usage:
  python startup.py                    # Interactive menu
  python startup.py prepare            # Prepare dataset
  python startup.py train              # Train model
  python startup.py predict [image]    # Predict image
  python startup.py api [port]         # Start API
  python startup.py validate           # Validate system
  python startup.py help               # Show help
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

REQUIRED_PACKAGES = ['tensorflow', 'keras', 'cv2', 'numpy', 'flask']
REQUIRED_FILES = [
    'train_complete.py',
    'predict_final.py',
    'app_api.py',
    'prepare_dataset.py',
    'disease_database.json'
]
REQUIRED_ARTIFACTS = [
    'artifacts/crop_disease_model.h5',
    'artifacts/crop_disease_model.keras',
    'artifacts/class_names.json'
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(" " * (40 - len(text)//2) + text)
    print("="*80 + "\n")

def print_section(text):
    """Print section header"""
    print(f"\n{text}")
    print("-" * 80)

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠ {text}")

def print_error(text):
    """Print error message"""
    print(f"✗ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ {text}")

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def check_python_version():
    """Check Python version"""
    print_section("Checking Python Version")
    
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.8+ required (found {version.major}.{version.minor})")
        return False

def check_required_files():
    """Check required files"""
    print_section("Checking Required Files")
    
    all_exist = True
    
    for filename in REQUIRED_FILES:
        if os.path.exists(filename):
            print_success(filename)
        else:
            print_warning(f"Missing: {filename}")
            all_exist = False
    
    return all_exist

def check_artifacts():
    """Check model artifacts"""
    print_section("Checking Model Artifacts")
    
    for artifact in REQUIRED_ARTIFACTS:
        if os.path.exists(artifact):
            size_mb = os.path.getsize(artifact) / (1024*1024)
            print_success(f"{artifact} ({size_mb:.1f} MB)")
        else:
            print_warning(f"Missing: {artifact}")
    
    # Check if at least one model exists
    model_exists = os.path.exists('artifacts/crop_disease_model.h5') or \
                   os.path.exists('artifacts/crop_disease_model.keras')
    
    return model_exists

def check_dataset():
    """Check dataset structure"""
    print_section("Checking Dataset")
    
    expected_classes = [
        "Brinjal_Healthy",
        "Brinjal_Little_Leaf",
        "Brinjal_Leaf_Spot",
        "Brinjal_Blight",
        "Grapes_Healthy",
        "Grapes_Black_Measles",
        "Grapes_Black_Rot",
        "Grapes_Isariopsis_Leaf_Spot"
    ]
    
    dataset_dir = "dataset"
    
    if not os.path.exists(dataset_dir):
        print_warning(f"Dataset directory not found: {dataset_dir}")
        return False
    
    total_images = 0
    
    for class_name in expected_classes:
        class_dir = os.path.join(dataset_dir, class_name)
        
        if not os.path.exists(class_dir):
            print_warning(f"Missing class: {class_name}")
            continue
        
        # Count images
        image_count = 0
        for item in Path(class_dir).rglob("*"):
            if item.suffix.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}:
                image_count += 1
        
        if image_count > 0:
            print_success(f"{class_name}: {image_count} images")
            total_images += image_count
        else:
            print_warning(f"{class_name}: 0 images")
    
    print_info(f"Total images: {total_images}")
    
    return total_images > 0

def validate_system():
    """Complete system validation"""
    print_header("SYSTEM VALIDATION")
    
    checks = [
        ("Python Version", check_python_version()),
        ("Required Files", check_required_files()),
        ("Model Artifacts", check_artifacts()),
        ("Dataset", check_dataset())
    ]
    
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    for name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:<30} {status}")
    
    all_pass = all(result for _, result in checks)
    
    print("="*80)
    
    if all_pass:
        print_success("\nSystem is ready for use!")
        return True
    else:
        print_warning("\nSome components are missing. See above for details.")
        return False

# ============================================================================
# OPERATION FUNCTIONS
# ============================================================================

def run_prepare_dataset():
    """Run dataset preparation"""
    print_header("PREPARING DATASET")
    
    try:
        subprocess.run([sys.executable, 'prepare_dataset.py'], check=True)
        return True
    except subprocess.CalledProcessError:
        print_error("Dataset preparation failed")
        return False

def run_train_model():
    """Run model training"""
    print_header("TRAINING MODEL")
    
    # Check dataset first
    if not check_dataset():
        print_error("\nDataset not ready. Please prepare dataset first:")
        print_info("  python startup.py prepare")
        return False
    
    try:
        subprocess.run([sys.executable, 'train_complete.py'], check=True)
        return True
    except subprocess.CalledProcessError:
        print_error("Training failed")
        return False

def run_predict(image_path):
    """Run single prediction"""
    print_header("PREDICTING DISEASE")
    
    if not os.path.exists(image_path):
        print_error(f"Image not found: {image_path}")
        return False
    
    # Check model
    if not os.path.exists('artifacts/crop_disease_model.h5') and \
       not os.path.exists('artifacts/crop_disease_model.keras'):
        print_error("Model not found. Please train first:")
        print_info("  python startup.py train")
        return False
    
    try:
        subprocess.run([sys.executable, 'predict_final.py', image_path], check=True)
        return True
    except subprocess.CalledProcessError:
        print_error("Prediction failed")
        return False

def run_api(port=5000):
    """Run API server"""
    print_header("STARTING API SERVER")
    
    # Check model
    if not os.path.exists('artifacts/crop_disease_model.h5') and \
       not os.path.exists('artifacts/crop_disease_model.keras'):
        print_error("Model not found. Please train first:")
        print_info("  python startup.py train")
        return False
    
    print_info(f"Starting API on http://localhost:{port}")
    print_info("Press Ctrl+C to stop")
    
    try:
        subprocess.run([sys.executable, 'app_api.py', str(port)])
    except KeyboardInterrupt:
        print_info("\nAPI stopped")
        return True
    except subprocess.CalledProcessError:
        print_error("API failed to start")
        return False

# ============================================================================
# INTERACTIVE MENU
# ============================================================================

def show_menu():
    """Show interactive menu"""
    print_header("CROP DISEASE PREDICTION SYSTEM")
    
    print("""
1. Validate System
2. Prepare Dataset
3. Train Model
4. Test Prediction
5. Start API Server
6. View Documentation
7. Exit

Select option (1-7):
""")

def interactive_menu():
    """Run interactive menu"""
    while True:
        choice = input(">>> ").strip()
        
        if choice == '1':
            validate_system()
        
        elif choice == '2':
            run_prepare_dataset()
        
        elif choice == '3':
            run_train_model()
        
        elif choice == '4':
            image = input("Enter image path: ").strip()
            if image:
                run_predict(image)
        
        elif choice == '5':
            port = input("Enter port (default 5000): ").strip()
            try:
                port = int(port) if port else 5000
                run_api(port)
            except ValueError:
                print_error("Invalid port number")
        
        elif choice == '6':
            print("\nOpening documentation...")
            if os.path.exists('COMPLETE_SETUP_GUIDE.md'):
                print_info("See COMPLETE_SETUP_GUIDE.md for detailed documentation")
            else:
                print_warning("Documentation file not found")
        
        elif choice == '7':
            print("\nGoodbye!")
            break
        
        else:
            print_error("Invalid option. Please try again.")
        
        print("\nPress Enter to continue...")
        input()

# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def show_help():
    """Show help message"""
    print(__doc__)
    print("""
EXAMPLES:
  python startup.py validate                 # Validate system
  python startup.py prepare                  # Prepare dataset
  python startup.py train                    # Train model
  python startup.py predict image.jpg        # Predict single image
  python startup.py api 5000                 # Start API on port 5000

WORKFLOWS:
  
  First time setup:
    1. python startup.py prepare
    2. python startup.py train
    3. python startup.py validate
  
  Testing predictions:
    1. python startup.py predict test.jpg
  
  Running API:
    1. python startup.py api 5000
    2. Visit http://localhost:5000
""")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        # Interactive mode
        interactive_menu()
    else:
        command = sys.argv[1].lower()
        
        if command == 'help' or command == '-h' or command == '--help':
            show_help()
        
        elif command == 'validate':
            validate_system()
        
        elif command == 'prepare':
            run_prepare_dataset()
        
        elif command == 'train':
            run_train_model()
        
        elif command == 'predict':
            if len(sys.argv) < 3:
                print_error("Please provide image path")
                print_info("Usage: python startup.py predict <image_path>")
            else:
                run_predict(sys.argv[2])
        
        elif command == 'api':
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
            run_api(port)
        
        else:
            print_error(f"Unknown command: {command}")
            show_help()

if __name__ == "__main__":
    main()
