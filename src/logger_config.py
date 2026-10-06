import logging
import sys
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

logger = logging.getLogger("file_manager")
logger.setLevel(logging.INFO)

_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

_console = logging.StreamHandler(sys.stdout)
_console.setFormatter(_formatter)
logger.addHandler(_console)

_file = logging.FileHandler("logs/app.log")
_file.setFormatter(_formatter)
logger.addHandler(_file)
