import logging
import logging.handlers


def local_logging(log_file, testdir):

    if testdir is not None:
        log = logging.getLogger(log_file)
        log.propagate = False
    else:
        log = logging.getLogger(log_file)
        log.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(created)f %(levelname)-2s %(message)s")

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    log.addHandler(file_handler)

    return log
