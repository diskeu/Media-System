from mysql.connector.aio import connect as aio_connect
from mysql.connector.aio.connection import MySQLConnection as aio_MySQLConnection

# Errors
from mysql.connector import (
    errorcode,
    Error as MysqlConnectorError
)
from mysql.connector.errors import (
    ProgrammingError,
    DatabaseError
)
import logging
from utils.type_helpers import to_int
from asyncio import sleep

# seting up logger
mysql_connection_logger = logging.getLogger(__name__)
mysql_connection_logger.setLevel(logging.DEBUG)

# setting up formatter
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

# setting up stream_handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(fmt=formatter)
stream_handler.setLevel(logging.DEBUG)

# setting up file_handler
file_handler = logging.FileHandler(filename="/Users/TimJelenz/Desktop/messenger/Backend/App/Logs/mysql_connection_log.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.WARNING)

# adding handlers
mysql_connection_logger.addHandler(stream_handler)
mysql_connection_logger.addHandler(file_handler)

async def connect(config_file_location: str, user: str | None = None, attempts: int = 1, delay: int = 2) -> aio_MySQLConnection | None:
    """
    ### Given a configuration-file location, returns a mysql connection object ###

    :param config_file_location: configuration-file location
    :type config_file_location: str
    :param user: If 'user' is provided, it's values will be used; otherwise, DEFAULT will be used.
    :type user: str | None
    :return: returns a mysql connection object
    :rtype: aio_MySQLConnection
    """
    def new_section(line: str, confg_dict: dict, cur_section_name: str) -> bool | None:
        """If the line contains a new section, return True; otherwise, return None and add the values to the section."""
        if line == " " or line == "\n": return
        elif "[" in line: return True
        else:
            try:
                k, v = line.split("=")
                k, v = to_int(k.strip()), to_int(v.strip())
                confg_dict[cur_section_name][k] = v
            except ValueError:                      # no key-value couple
                mysql_connection_logger.exception("Can't unbound line, no key-value couple")
        return
    
    def create_section(line: str, confg_dict: dict) -> None:
        """Creates a section, in the confg_dict"""
        section_name = line.strip()                 # removing (trailing & leading) whitespaces and line breaks
        section_name = section_name.strip("[]")     # removing parentheses
        confg_dict[section_name] = {}
        return section_name
    
    def config_file_parser(confg_f_lines: list) -> dict[dict]:
        """Creates a dictionary from the lines of a config file"""
        confg_dict: dict = {}
        cur_section: bool = False
        for line in confg_f_lines:
            if cur_section:
                if new_section(line=line, confg_dict=confg_dict, cur_section_name=section_name):
                    section_name = create_section(line=line, confg_dict=confg_dict)

            elif "[" in line:
                section_name = create_section(line=line, confg_dict=confg_dict)
                cur_section = True
        return confg_dict

    # Getting lines from the config file
    try:
        with open(config_file_location, "r") as confg_f:
            confg_f_lines: list = confg_f.readlines()
    except FileNotFoundError:
        mysql_connection_logger.exception("Can't open file")
    
    # Calling function to parse lines into dictionary format
    confg_dict: dict[dict] = config_file_parser(confg_f_lines)

    # Combining both dictionarys
    confg: dict = confg_dict.get("DEFAULT")
    if user:
        user: dict = confg_dict.get(user)
        confg = confg | user

    # Connecting to mysql using the attempts, delay and config dictionary
    attempt = 1
    while attempt <= attempts:
        try:
            return await aio_connect(
                connection_timeout=3,
                read_timeout=8,
                write_timeout=8,
                **confg
            )
        except MysqlConnectorError as err:
            # Syntacx error
            if isinstance(err, ProgrammingError):
                print(err)
                mysql_connection_logger.exception("Syntax error or table doesn't exist")
                return None
            
            # Permission error
            elif getattr(err, "errno", None) == errorcode.ER_ACCESS_DENIED_ERROR:
                mysql_connection_logger.exception("Permission denied, check username or password")
                return None
            
            # Host/Connection error -> Retry
            elif getattr(err, "errno", None) in (errorcode.CR_CONN_HOST_ERROR, errorcode.CR_CONNECTION_ERROR):
                if attempt == attempts:
                    # attempts to reconnect failed, returning None
                    mysql_connection_logger.exception("Reconnecting failed, existing with error %s", err)
                    return None
                else:
                    mysql_connection_logger.warning("Attempt (%d/%d) to reconnect, Retrying in %d seconds, Exception: %s", attempt, attempts, attempts**delay, err)
                    await sleep(attempts**delay)
                    attempt += 1
                    continue

            # Database / Connection Error
            elif isinstance(err, DatabaseError):
                mysql_connection_logger.exception("Database does not exist, or connection timout occured")
                return None
            
            else: raise err # raise other errors