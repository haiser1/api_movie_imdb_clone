import json
import logging
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """
    Formatter class that formats log records into JSON strings.
    """

    def format(self, record):
        """
        Formats the log record into a JSON string.

        Args:
            record (logging.LogRecord): The log record to be formatted.

        Returns:
            str: The log record formatted as a JSON string.

        This function takes a log record and formats it into a JSON string. It starts
        by extracting the basic attributes from the record log. It then adds details
        about where the log originated from. It also includes optional fields provided
        in the 'extra' parameter of the log record. Finally, it formats any
        exceptions that occurred during the logging process.
        """
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }

        log_record.update(
            {
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
        )

        # extra data
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        # exception format
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_record)


class JsonLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        if "extra" in kwargs:
            kwargs["extra"] = {"extra_data": kwargs["extra"]}
        return msg, kwargs


json_logger = JsonLoggerAdapter(logging.getLogger("gunicorn.error"), {})


def init_logger(app=None):
    """
    Initialize the application logger.

    Configures a logger named "gunicorn.error" with the log level
    specified in app.config["LOG_LEVEL"]. If no app is provided,
    defaults to INFO.

    Args:
        app: Flask application instance (optional).

    Returns:
        JsonLoggerAdapter: The configured JSON logger adapter.
    """
    global json_logger

    log_level = "INFO"
    if app:
        log_level = app.config.get("LOG_LEVEL", "INFO")

    level = getattr(logging, log_level.upper(), logging.INFO)

    logger = logging.getLogger("gunicorn.error")
    logger.setLevel(level)

    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        handler.setLevel(level)
        logger.addHandler(handler)
    else:
        # Update level pada handler yang sudah ada
        for h in logger.handlers:
            if isinstance(h, logging.StreamHandler):
                h.setLevel(level)

    json_logger = JsonLoggerAdapter(logger, {})
    return json_logger
