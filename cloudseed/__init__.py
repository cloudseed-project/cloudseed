__title__ = 'cloudseed'
__version__ = '0.0.1'


# logging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)

formatter = logging.Formatter('[%(levelname)s] : %(name)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)
