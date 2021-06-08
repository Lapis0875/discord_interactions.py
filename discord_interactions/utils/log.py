from logging import CRITICAL, FATAL, ERROR, WARN, WARNING, INFO, DEBUG, NOTSET
import logging
from sys import stdout


__all__ = (
    'CRITICAL',
    'FATAL',
    'ERROR',
    'WARN',
    'WARNING',
    'INFO',
    'DEBUG',
    'NOTSET',
    'get_stream_logger'
)


def get_stream_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger: logging.Logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler(stdout)
    handler.setFormatter(
        logging.Formatter(
            style='{',
            fmt='[{asctime}] [{levelname}] {name}: {message}'
        )
    )
    logger.addHandler(handler)
    return logger
