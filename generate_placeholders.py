"""
Generate placeholder images for missing dataset classes
This creates synthetic images for classes that don't have real data yet.
Replace these with real images later for better accuracy.
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def create_placeholder_images(class_name, num_images=100, size=(224, 224)):
    """Create synthetic placeholder images for a class"""
    
    class_path = f'Dataset/{class_name}'
    os.makedirs(class_path, exist_ok=True)
    
    logger.info(f"\nGenerating placeholder images for: {class_name}")
    logger.info(f"Target: {num_images} images at {size}x{size}")
    
    for i in range(num_images):
        # Create random background (simulating leaf texture)
        if 'Healthy' in class_name:
            # Green tones for healthy plants
            base_color = (50 + np.random.randint(-20, 20),
                         100 + np.random.randint(-20, 20),
                         50 + np.random.randint(-20, 20))
        else:
            # Brown/yellow tones for diseased plants
            base_color = (100 + np.random.randint(-20, 20),
                         80 + np.random.randint(-20, 20),
                         40 + np.random.randint(-20, 20))
        
        # Create image
        img = Image.new('RGB', size, base_color)
        draw = ImageDraw.Draw(img)
        
        # Add some texture/noise
        pixels = img.load()
        for _ in range(1000):
            x = np.random.randint(0, size[0])
            y = np.random.randint(0, size[1])
            noise = np.random.randint(-30, 30)
            r = max(0, min(255, base_color[0] + noise))
            g = max(0, min(255, base_color[1] + noise))
            b = max(0, min(255, base_color[2] + noise))
            pixels[x, y] = (r, g, b)
        
        # Add disease spots if applicable
        if 'Healthy' not in class_name:
            for _ in range(np.random.randint(3, 10)):
                x = np.random.randint(20, size[0]-20)
                y = np.random.randint(20, size[1]-20)
                radius = np.random.randint(10, 30)
                spot_color = (60 + np.random.randint(-20, 20),
                             40 + np.random.randint(-20, 20),
                             30 + np.random.randint(-20, 20))
                draw.ellipse([x-radius, y-radius, x+radius, y+radius],
                           fill=spot_color, outline=spot_color)
        
        # Save image
        filename = f'{class_name}_placeholder_{i:04d}.jpg'
        filepath = os.path.join(class_path, filename)
        img.save(filepath, quality=85)
        
        if (i + 1) % 20 == 0:
            logger.info(f"  Progress: {i+1}/{num_images}")
    
    logger.info(f"✓ {class_name}: {num_images} placeholder images created")


def main():
    """Generate placeholder images for all missing classes"""
    
    logger.info("="*80)
    logger.info("GENERATING PLACEHOLDER IMAGES FOR MISSING CLASSES")
    logger.info("="*80)
    logger.info("\nWARNING: These are synthetic placeholder images for testing only.")
    logger.info("Replace with real disease images for production use.\n")
    
    missing_classes = [
        'Brinjal_Healthy',
        'Brinjal_Leaf_Spot',
        'Brinjal_Blight',
        'Grapes_Healthy'
    ]
    
    for class_name in missing_classes:
        # Check if class already has images
        class_path = f'Dataset/{class_name}'
        existing = len([f for f in os.listdir(class_path) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))])
        
        if existing > 50:
            logger.info(f"⊘ {class_name}: Already has {existing} images, skipping")
            continue
        
        create_placeholder_images(class_name, num_images=100)
    
    logger.info("\n" + "="*80)
    logger.info("✓ PLACEHOLDER GENERATION COMPLETE")
    logger.info("="*80)
    logger.info("\nNEXT STEPS:")
    logger.info("1. Run training: python train_unified.py")
    logger.info("2. Test predictions: python predict.py path/to/test_image.jpg")
    logger.info("3. Later: Replace placeholder images with real disease photos\n")


if __name__ == '__main__':
    main()
