import logging
from datetime import datetime
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

def log_session_header():
    """Log a professional session header with date to distinguish automation runs."""
    current_time = datetime.now()
    date_str = current_time.strftime('%m/%d/%Y')
    time_str = current_time.strftime('%H:%M:%S')
    
    # Create professional session header
    separator = "*" * 50
    header_lines = [
        "",  # Empty line for spacing
        separator,
        f"   {date_str} COMPASS AUTOMATION SESSION",
        f"   Started at {time_str}",
        separator,
        ""  # Empty line for spacing
    ]
    
    # Write directly to file to include the header
    with open("Compass.log", "a", encoding="utf-8") as f:
        for line in header_lines:
            f.write(f"{line}\n")

# Get log level and format from config
log_level = get_config("logging.level", "INFO").upper()
log_format_raw = get_config("logging.format", "[%(levelname)s] [%(asctime)s] %(message)s")

if "%(name)s" in log_format_raw:
    # Remove logger-name tokens to avoid noisy output like [mc.automation]
    log_format = log_format_raw.replace("[%(name)s]", "").replace("%(name)s", "").replace("  ", " ").strip()
else:
    log_format = log_format_raw

# Create one logger instance for the whole project
log = logging.getLogger("mc.automation")
log.setLevel(getattr(logging, log_level, logging.INFO))

# Clear existing handlers to prevent duplicate or unwanted output
if log.handlers:
    for handler in log.handlers:
        log.removeHandler(handler)

# Attach handler/formatter only once
# Console handler obeys configured log level (shows only time for readability)
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, log_level, logging.INFO))
console_handler.setFormatter(ColorFormatter(log_format, datefmt="%H:%M:%S"))
log.addHandler(console_handler)

# File handler captures DEBUG and above with time only (date shown in session header)
file_handler = logging.FileHandler("Compass.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format, datefmt="%H:%M:%S"))
log.addHandler(file_handler)