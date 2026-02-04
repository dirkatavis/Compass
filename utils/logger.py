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
log_level = get_config("logging.level", "INFO").upper()
log_format_raw = get_config("logging.format", "[%(levelname)s] [%(asctime)s] %(message)s")

# Tokens to identify for suppression (placeholders and literal strings)
suppress_targets = ["%(name)s", "mc.automation"]
log_format = log_format_raw

# Remove tokens and literal names to avoid noisy output like [mc.automation]
for target in suppress_targets:
    log_format = log_format.replace(f"[{target}]", "").replace(target, "")

# Cleanup whitespace resulting from removals
log_format = log_format.replace("  ", " ").strip()

# Create one logger instance for the whole project
log = logging.getLogger("mc.automation")
log.setLevel(getattr(logging, log_level, logging.INFO))

# Clear existing handlers to prevent duplicate or unwanted output
if log.handlers:
    for handler in log.handlers:
        log.removeHandler(handler)

# Attach handler/formatter only once
# Console handler obeys configured log level
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, log_level, logging.INFO))
console_handler.setFormatter(ColorFormatter(log_format, datefmt="%H:%M:%S"))
log.addHandler(console_handler)

# File handler captures DEBUG and above with same format
file_handler = logging.FileHandler("Compass.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format, datefmt="%H:%M:%S"))
log.addHandler(file_handler)