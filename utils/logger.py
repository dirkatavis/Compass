
import logging
import os
from config.config_loader import get_config

class ColorFormatter(logging.Formatter):
	COLORS = {
		"DEBUG": "\033[36m",    # gray
		"INFO": "\033[37m",     # cyan
		"WARNING": "\033[33m",  # yellow
		"ERROR": "\033[31m",    # red
		"CRITICAL": "\033[41m"  # red background
	}
	RESET = "\033[0m"

	def format(self, record):
		color = self.COLORS.get(record.levelname, self.RESET)
		message = super().format(record)
		return f"{color}{message}{self.RESET}"


# Create one logger instance for the whole project
log = logging.getLogger("mc.automation")
# Get log level from config, fallback to INFO if not set or invalid
_level_str = str(get_config("log_level", "INFO")).upper()
_level = getattr(logging, _level_str, logging.INFO)
log.setLevel(_level)

# Ensure project-level logs directory exists (project root/logs)
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
logs_dir = os.path.join(repo_root, "logs")
if not os.path.exists(logs_dir):
	try:
		os.makedirs(logs_dir, exist_ok=True)
	except Exception:
		# If we can't create logs dir, continue and rely on console logging
		pass

# Attach handlers only once
if not log.handlers:
	# Console (colored) handler
	handler = logging.StreamHandler()
	formatter = ColorFormatter(
		"[%(levelname)s] [%(name)s] [%(asctime)s] %(message)s",
		datefmt="%H:%M:%S"
	)
	handler.setFormatter(formatter)
	log.addHandler(handler)

# File handler (non-colored) - add if missing
file_log_path = os.path.join(logs_dir, "compass_automation.log")
if not any(isinstance(h, logging.FileHandler) for h in log.handlers):
	try:
		file_handler = logging.FileHandler(file_log_path, encoding="utf-8")
		file_formatter = logging.Formatter(
			"[%(levelname)s] [%(name)s] [%(asctime)s] %(message)s",
			datefmt="%Y-%m-%d %H:%M:%S",
		)
		file_handler.setFormatter(file_formatter)
		file_handler.setLevel(logging.DEBUG)
		log.addHandler(file_handler)
	except Exception:
		# If file handler can't be created (permissions, path), continue with console-only logging
		log.warning(f"[LOGGER] Could not create file handler at {file_log_path}")
