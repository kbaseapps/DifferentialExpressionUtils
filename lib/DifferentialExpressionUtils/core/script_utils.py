import logging
import os

'''
A utility python module containing a set of methods necessary for this kbase
module.
'''

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

def create_logger(log_dir,name):
    """Create a logger

    args: name (str): name of logger

    returns: logger (obj): logging.Logger instance
    """
    logger = logging.getLogger(name)
    fmt = logging.Formatter('%(asctime)s - %(process)d - %(name)s - '
                            ' %(levelname)s -%(message)s')
    hdl = logging.FileHandler(os.path.join(log_dir,name+'.log'))
    hdl.setFormatter(fmt)

    logger.addHandler(hdl)

    return logger

def log(message, level=logging.INFO, logger=None):
    if logger is None:
        if level == logging.DEBUG:
            print('\nDEBUG: ' + message + '\n')
        elif level == logging.INFO:
            print('\nINFO: ' + message + '\n')
        elif level == logging.WARNING:
            print('\nWARNING: ' + message + '\n')
        elif level == logging.ERROR:
            print('\nERROR: ' + message + '\n')
        elif level == logging.CRITICAL:
            print('\nCRITICAL: ' + message + '\n')
    else:
        logger.log(level, '\n' + message + '\n')

def check_sys_stat(logger):
    check_disk_space(logger)
    check_memory_usage(logger)
    check_cpu_usage(logger)

def check_disk_space(logger):
    runProgram(logger=logger, progName="df", argStr="-h")


def check_memory_usage(logger):
    runProgram(logger=logger, progName="vmstat", argStr="-s")


def check_cpu_usage(logger):
    runProgram(logger=logger, progName="mpstat", argStr="-P ALL")
