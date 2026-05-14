import os
import sys

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Step 1: Testing imports...")
try:
    from src.Components.data_ingestion import DataIngestion
    from src.Components.data_transformation import DataTransformation
    from src.Components.model_trainer import ModelTrainer
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print("\nStep 2: Data Ingestion...")
try:
    ingestion = DataIngestion()
    train_dir, test_dir = ingestion.initiate_data_ingestion()
    print(f"✅ Data ingestion done: train={train_dir}, test={test_dir}")
except Exception as e:
    print(f"❌ Data ingestion failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Data Transformation...")
try:
    dt = DataTransformation(train_dir, test_dir)
    train_data, test_data = dt.initiate_data_transformation()
    print(f"✅ Data transformation done")
    print(f"   Train batches: {len(train_data)}")
    print(f"   Test batches: {len(test_data)}")
    print(f"   Classes: {list(train_data.class_indices.keys())}")
except Exception as e:
    print(f"❌ Data transformation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 4: Model Building...")
try:
    trainer = ModelTrainer()
    num_classes = len(train_data.class_indices)
    model = trainer.build_model(num_classes)
    print(f"✅ Model built successfully")
    print(f"   Total params: {model.count_params():,}")
except Exception as e:
    print(f"❌ Model building failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 5: Getting callbacks...")
try:
    callbacks = trainer.get_callbacks()
    print(f"✅ Callbacks created: {len(callbacks)} callbacks")
except Exception as e:
    print(f"❌ Callbacks failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 6: Starting training (first epoch only for testing)...")
try:
    print("   Attempting model.fit()...")
    history = model.fit(
        train_data,
        validation_data=test_data,
        epochs=1,  # Just 1 epoch for testing
        callbacks=callbacks,
        verbose=1
    )
    print(f"✅ Training completed!")
    print(f"   Accuracy: {history.history.get('accuracy', [None])[0]}")
except Exception as e:
    print(f"❌ Training failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ ALL STEPS COMPLETED SUCCESSFULLY!")
