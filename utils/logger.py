import logging
from config.config_loader import get_config

class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",    # cyan
        "INFO": "\033[37m",     # white
        "WARNING": "\033[33m",  # yellow
        "ERROR": "\033[31m",    # red
        "CRITICAL": "\033[41m"  # red background
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"

# Get log level and format from config
log_level = get_config('logging.level', 'INFO').upper()
log_format = get_config('logging.format', "[%(levelname)s] [%(name)s] [%(asctime)s] %(message)s")

# Create one logger instance for the whole project
log = logging.getLogger("mc.automation")
log.setLevel(logging.DEBUG) # Set logger to capture all levels

# Attach handler/formatter only once
if not log.handlers:
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # Set console to INFO
    console_formatter = ColorFormatter(
        log_format,
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    log.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler("Compass.log", encoding='utf-8')
    file_handler.setLevel(logging.DEBUG) # Set file to DEBUG
    file_formatter = logging.Formatter(log_format, datefmt="%H:%M:%S")
    file_handler.setFormatter(file_formatter)
    log.addHandler(file_handler)