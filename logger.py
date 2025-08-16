import logging
import os

os.makedirs('log', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("log/logger.log", mode='w', encoding='utf-8'),  # 덮어쓰기
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)