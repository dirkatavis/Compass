import logging

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
log.setLevel(logging.DEBUG)

# Attach handler/formatter only once
if not log.handlers:
	handler = logging.StreamHandler()
	formatter = ColorFormatter(
		"[%(levelname)s] [%(name)s] [%(asctime)s] %(message)s",
		datefmt="%H:%M:%S"
	)
	handler.setFormatter(formatter)
	log.addHandler(handler)
