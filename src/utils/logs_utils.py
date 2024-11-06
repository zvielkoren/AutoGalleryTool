import logging


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs.log'),
            logging.StreamHandler()
        ]
    )


def get_logger(name):
    """
    Get a logger with the given name.
    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The logger object.


    """

    logger = logging.getLogger(name)
    return logger
