import datetime
import logging
import os
import sys

import pytz

SYS_LOG_HANDLER_NAME = "sys"
date_timezone = pytz.timezone('US/Pacific')
date_formatting_in_filename = "%Y_%m_%d_%H_%M_%S"
error_logging_level = logging.ERROR


class PSTFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=None):
        super(PSTFormatter, self).__init__(fmt, datefmt)
        self.tz = tz

    def formatTime(self, record, datefmt=None):  # noqa: N802
        """

        :param record:
        :param datefmt:
        :return:
        """
        dt = datetime.datetime.fromtimestamp(record.created, self.tz)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return str(dt)


date_formatting_in_log = '%Y-%m-%d %H:%M:%S'

sys_stream_formatting = PSTFormatter(
    '%(asctime)s = %(levelname)s = %(name)s = %(message)s', date_formatting_in_log, tz=date_timezone
)
warn_logging_level = logging.WARNING

REDIRECT_STD_STREAMS = True


class WalleWarnStreamHandler(logging.StreamHandler):
    def emit(self, record):
        if record.levelno < error_logging_level:
            super().emit(record)


class WalleDebugStreamHandler(logging.StreamHandler):
    def emit(self, record):
        if record.levelno < warn_logging_level:
            super().emit(record)


class Loggers:
    loggers = []
    logger_list_indices = {}

    @classmethod
    def get_logger(cls, logger_name):
        """
        Initiates and returns a logger for the specific logger_name
        :param logger_name: the name to assign to the returned logic
        :return:the logger
        """
        if logger_name == SYS_LOG_HANDLER_NAME:
            return cls._setup_sys_logger()
        else:
            return cls._setup_logger(logger_name)

    @classmethod
    def _setup_sys_logger(cls):
        """
        Creates a sys logger that directs anything going to sys.stdout/err to a log file
        and the stream as well
        :return: the sys logger
        """
        date = datetime.datetime.now(date_timezone).strftime(date_formatting_in_filename)
        if not os.path.exists(f"logs/{SYS_LOG_HANDLER_NAME}"):
            os.makedirs(f"logs/{SYS_LOG_HANDLER_NAME}")
        if not os.path.exists(f"logs/{SYS_LOG_HANDLER_NAME}"):
            os.makedirs(f"logs/{SYS_LOG_HANDLER_NAME}")

        sys_logger = logging.getLogger(SYS_LOG_HANDLER_NAME)
        sys_logger.setLevel(logging.DEBUG)

        debug_log_file_absolute_path = (
            f"logs/{SYS_LOG_HANDLER_NAME}/{date}_debug.log"
        )
        sys_stream_warn_log_file_absolute_path = (
            f"logs/{SYS_LOG_HANDLER_NAME}/{date}_warn.log"
        )
        sys_stream_error_log_file_absolute_path = (
            f"logs/{SYS_LOG_HANDLER_NAME}/{date}_error.log"
        )

        # ensures that anything printed to this logger at level DEBUG or above goes to the specified file
        debug_filehandler = logging.FileHandler(debug_log_file_absolute_path)
        debug_filehandler.setLevel(logging.DEBUG)
        sys_logger.addHandler(debug_filehandler)

        # ensures that anything printed to this logger at level WARN or above goes to the specified file
        warn_filehandler = logging.FileHandler(sys_stream_warn_log_file_absolute_path)
        warn_filehandler.setLevel(warn_logging_level)
        sys_logger.addHandler(warn_filehandler)

        # ensures that anything printed to this logger at level ERROR or above goes to the specified file
        error_filehandler = logging.FileHandler(sys_stream_error_log_file_absolute_path)
        error_filehandler.setLevel(error_logging_level)
        sys_logger.addHandler(error_filehandler)

        # ensures that anything from the log goes to the stdout
        if REDIRECT_STD_STREAMS:
            sys.stdout = sys.__stdout__
        sys_stdout_stream_handler = WalleDebugStreamHandler(sys.stdout)
        sys_stdout_stream_handler.setLevel(logging.DEBUG)
        sys_logger.addHandler(sys_stdout_stream_handler)
        if REDIRECT_STD_STREAMS:
            sys.stdout = LoggerWriter(sys_logger.info)

        sys_std_warn_stream_handler = WalleWarnStreamHandler(sys.stdout)
        sys_std_warn_stream_handler.setLevel(warn_logging_level)
        sys_logger.addHandler(sys_std_warn_stream_handler)

        if REDIRECT_STD_STREAMS:
            sys.stderr = sys.__stderr__
        sys_stderr_stream_handler = logging.StreamHandler(sys.stderr)
        sys_stderr_stream_handler.setLevel(error_logging_level)
        sys_logger.addHandler(sys_stderr_stream_handler)
        if REDIRECT_STD_STREAMS:
            sys.stderr = LoggerWriter(sys_logger.error)

        return (
            sys_logger, debug_log_file_absolute_path, sys_stream_warn_log_file_absolute_path,
            sys_stream_error_log_file_absolute_path
        )

    @classmethod
    def _setup_logger(cls, service_name):
        """
        Creates a logger for the specified service that prints to a file and the sys.stdout
        and sys.stderr
        :param service_name: the name of the service that is initializing the logger
        :return: the logger
        """
        date = datetime.datetime.now(date_timezone).strftime(date_formatting_in_filename)
        if not os.path.exists(f"logs/{service_name}"):
            os.makedirs(f"logs/{service_name}")
        debug_log_file_absolute_path = f"logs/{service_name}/{date}_debug.log"
        warn_log_file_absolute_path = f"logs/{service_name}/{date}_warn.log"
        error_log_file_absolute_path = f"logs/{service_name}/{date}_error.log"

        logger = logging.getLogger(service_name)
        logger.setLevel(logging.DEBUG)

        debug_filehandler = logging.FileHandler(debug_log_file_absolute_path)
        debug_filehandler.setLevel(logging.DEBUG)
        debug_filehandler.setFormatter(sys_stream_formatting)
        logger.addHandler(debug_filehandler)

        warn_filehandler = logging.FileHandler(warn_log_file_absolute_path)
        warn_filehandler.setFormatter(sys_stream_formatting)
        warn_filehandler.setLevel(warn_logging_level)
        logger.addHandler(warn_filehandler)

        error_filehandler = logging.FileHandler(error_log_file_absolute_path)
        error_filehandler.setFormatter(sys_stream_formatting)
        error_filehandler.setLevel(error_logging_level)
        logger.addHandler(error_filehandler)

        sys_stdout_stream_handler = WalleDebugStreamHandler(sys.stdout)
        sys_stdout_stream_handler.setFormatter(sys_stream_formatting)
        sys_stdout_stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(sys_stdout_stream_handler)

        sys_std_warn_stream_handler = WalleWarnStreamHandler(sys.stdout)
        sys_std_warn_stream_handler.setFormatter(sys_stream_formatting)
        sys_std_warn_stream_handler.setLevel(warn_logging_level)
        logger.addHandler(sys_std_warn_stream_handler)

        sys_sterr_stream_handler = logging.StreamHandler()
        sys_sterr_stream_handler.setFormatter(sys_stream_formatting)
        sys_sterr_stream_handler.setLevel(error_logging_level)
        logger.addHandler(sys_sterr_stream_handler)

        return (
            logger, debug_log_file_absolute_path, warn_log_file_absolute_path, error_log_file_absolute_path
        )


class LoggerWriter:
    def __init__(self, level):
        """
        User to direct the sys.stdout/err to the specified log level
        :param level:
        """
        self.level = level

    def write(self, message):
        """
        writes from the sys.stdout/err to the logger object for sys_logger
        :param message: the message to write to the log
        :return:
        """
        if message != '\n':
            # removing newline that is created [I believe] when stdout automatically adds a newline to the string
            # before passing it to this method, and self.level itself also adds a newline
            message = message[:-1] if message[-1:] == "\n" else message
            self.level(message)

    def flush(self):
        pass
