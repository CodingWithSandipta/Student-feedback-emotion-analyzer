"""
Training entry point script.
Run this from the backend directory to train the Bi-LSTM model.
"""
import sys
import logging
from pathlib import Path

# Ensure the backend directory is in path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting Bi-LSTM training pipeline...")
    logger.info("Dataset: GoEmotions (Google Research) via HuggingFace")
    logger.info("This may take 10-30 minutes depending on hardware.\n")

    try:
        from ml.train import train_model
        config = train_model()
        logger.info("\n✓ Training complete!")
        logger.info(f"  Test Accuracy: {config.get('test_accuracy', 'N/A'):.4f}")
        logger.info(f"  Epochs trained: {config.get('actual_epochs', 'N/A')}")
        logger.info(f"  Training samples: {config.get('train_samples', 'N/A')}")
        logger.info("\nModel artifacts saved to backend/models/")
        logger.info("Reports saved to backend/reports/")
        logger.info("\nYou can now start the application with start_project.bat")
    except RuntimeError as e:
        logger.error(f"\n✗ Training failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n✗ Unexpected error: {e}", exc_info=True)
        sys.exit(1)
