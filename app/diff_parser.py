import logging

# Configure logging
def configure_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

logger = configure_logging()

# Inside your validate_issues_in_batch function:

def validate_issues_in_batch(...):
    # ... existing code ...
    for reason in validation_drop_reasons:
        logger.debug("Validation drop reason: %s", reason)
    # ... existing code ...
