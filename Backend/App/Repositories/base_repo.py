# base repo with functions that can be used by other repos
from __future__ import annotations
from ....utils.type_helpers import check_type
from ....utils.sql_helpers import format_value
from ....utils.sentinel import DEFAULT
from types import GeneratorType
from mysql.connector.errors import (
    OperationalError,
    IntegrityError,
    ProgrammingError,
    DatabaseError,
    InternalError,
    DataError,
    Error as MysqlBaseError
)
from ..Exceptions.DB_Exceptions import (
    QuerySyntaxError,
    ExistingAttributeError,
    ModelError,
    SqlReturnTypeError,
)
from ..Models.base_model import BaseModel as Model
from mysql.connector.aio.connection import MySQLConnection as aio_MySQLConnection
from mysql.connector.aio.cursor import MySQLCursor
from typing import Iterable
import inspect

class BaseRepo():
    """Base repo with helpers that can be used by other classes"""
    def __init__(self, logger):
        self.logger = logger

    class RepoError():
        """defining Repo error that'll get returned from handle_db_error"""
        error_table: dict = {
            1: MysqlBaseError,
            2: DatabaseError,
            3: ModelError,
            4: OperationalError,
            5: SqlReturnTypeError,
            6: InternalError,
            7: QuerySyntaxError,
            8: ExistingAttributeError,
            9: TypeError,
            10: DataError,
            11: Exception # Any kind of exception
        }
        def __init__(self, succes: bool, error_code: int, message: str, exception: Exception):
            self.succes = succes
            self.error_code = error_code
            self.message = message
            self.exception = exception

    def handle_db_error(self, err: Exception) -> RepoError:
        """Handles common DB errors and returns RepoError"""

        # logg exeption
        self.logger.exception("Exception occured: %s", err)

        # MySQL server encounters an internal error, for example, when a deadlock occurred
        if isinstance(err, InternalError):
            return self.RepoError(False, 6, "Internal error - deadlock occured", err)

        # Value already exists
        if isinstance(err, IntegrityError):
            return self.RepoError(False, 8, "Attributes Already Exist", err)
        
        # Syntax Error
        elif isinstance (err, ProgrammingError):
            return self.RepoError(False, 7, "Syntax error in Query", err)
        
        # Network / Timeout error -> too many connections; a host name could not be resolved; bad handshake; server is shutting down, communication errors
        elif isinstance(err, OperationalError):
            return self.RepoError(False, 4, "Network / Timeout error", err)
        
        # DataError -> This exception is raised when there were problems with the data
        elif isinstance(err, DataError):
            return self.RepoError(False, 10, "DataError", err)
        
        # DataBase errors
        elif isinstance(err, DatabaseError):
            return self.RepoError(False, 2, "Other DataBase Error", err)
        
        # Other Errors
        else: return self.RepoError(False, 11, "Error -> check Exception for more info", err)

    async def create_cursor_obj(self, cnx: aio_MySQLConnection, dict_format: bool = True) -> MySQLCursor | RepoError:
        """Given a Connection returns a cursor object or RepoError"""
        # reconnecting to DB and defining cursor
        if not await cnx.is_connected(): await cnx.reconnect()
        try:
            # returning in appropriate format
            return await cnx.cursor(dictionary=True) if dict_format else await cnx.cursor()
        except OperationalError as err:
            return self.RepoError(
                False,
                4,
                "Network / Timeout error",
                err
        )
    async def execute_write(self, query: str, *values, last_insert_id: bool = False) -> None | RepoError | int:
        """
        Given a sql insert/update/delete - query and values, executes the query\n
        returns None | RepoError
        """

        # getting cursor obj
        cursor = await self.create_cursor_obj(self.cnx)
        try:
            await cursor.execute(query, values)   # replaces %s with actual values
            if last_insert_id:
                last_insert_id = cursor.lastrowid
            else: last_insert_id = None
            
        except MysqlBaseError as err:
            self.logger.exception("Something in cursor execution went wrong, returning RepoError")
            return self.handle_db_error(err)
        
        finally:
            await self.cnx.commit()
            await cursor.close()

        return last_insert_id
        
    async def execute_read(self, query, *values) -> list[dict[any]] | RepoError:
        """
        Given a sql select - query and values, executes the query\n
        returns the cursor return in dict format | RepoError
        """
        # getting cursor
        cursor = await self.create_cursor_obj(self.cnx)
        try:
            await cursor.execute(query, values)
            rows: dict = await cursor.fetchall()
        except MysqlBaseError as err:
            self.logger.exception(
                "Something in cursor execution went wrong, returning RepoError"
            )
            return self.handle_db_error(err)
        finally:
            await cursor.close()
        return rows

    def check_pk_val(self, primary_keys: dict) -> None | RepoError:
        """Small help func that checks wether the primary keys-dict correspond to [str: int] and logs the errors, returns None|RepoError"""
        for pk_name, pk_id in primary_keys.items():
            if type(pk_name) != str or type(pk_id) != int:
                self.logger.warning(
                    "Wrong type of primary_key, "
                    "prefered type: tuple[str, int], "
                    f"given type: [{type(pk_name), ",", type(pk_id)}"
                )
                return self.RepoError(
                    False,
                    9,
                    "Wrong type",
                    TypeError(
                        "Wrong type of primary_key, "
                        "prefered type: tuple[str, int], "
                        f"given type: [{type(pk_name), ",", type(pk_id)}"
                    )
                )
    async def get_all_enriched(
        self,
        table: str,
        primary_keys: tuple[tuple[str, ...] | list[tuple[str, ...]] | any, list[tuple[any, ...]]] | None = None,
        joins: list[tuple[str, str]] = None,
        where_statement: str = None,
        condition: str = None,
        values: Iterable | None = None,
        columns: Iterable = None
    ) -> list[dict[any]] | RepoError:
        """
        Given a table and primary_keys returns all necessary information from the specified columns\n
        Primary Keys have to be in example format -> (("post_id", "community_id"), [("1", "10"), ("2", "15"), ("3", "20")]) or None\n
        NOTE:
            - In contrast to the normal get_info function it is intended to have acces to other columns via. JOIN.\n
            - It is built for more than one post and the return isn't intendet to be formatted into Models\n
            - If prmary_keys[0] is only 1 value, parse an non-iterable value\n
            - values 'll be added in order auto-generated primary key values -> specified values\n

        ## joins ##
        #### To use columns from other Tables you have to type a join statement into the joins parameter ####
        The joins have to be formatted like this\n
        joins = [
            ("INNER JOIN votes v", "p.post_id = v.post_id"),
            ("LEFT JOIN images i", "p.post_id = i.post_id")
        ]\n
        NOTE: Joins should'nt contain %s placeholders
        ## where_statement ##
        additional where statement that 'll get added
        
        ## condition ##
        Additonal conditon that 'll be added after the primary - key statement\n
        Condition should be formatted with %s -> 'll be later replaced with the values (the formatt vals of %s need to be given into values parm)

        ## Returns: ###
        Returns the sql connector return, in dict format | RepoError.
        """
        if not columns: columns = []

        # JOIN
        join_statement = ""
        if joins:
            join_statement = " ".join(f"{j[0]} ON {j[1]}" for j in joins)
        
        # collect all WHERE conditions
        where_statement_all = []
        combined_values = []

        def convert_tuples_format(tuple_list: list[tuple[any]]) -> str:
            """
            Function that converts list of tuples into format ((1, 2), (3, 4)...)\n
            and adds each value formatted into values
            """
            def add_to_values(val: any) -> str:
                """Function that adds the appropriate type of the value to combined_values and always returns %s"""
                combined_values.append(format_value(val))
                return "%s"
            
            # converting tuples into format ((1, 2), (3, 4)...)
            place_holder_vals = (', '.join(add_to_values(v) for v in t) for t in tuple_list)

            if not one_key:
                return f"({', '.join(place_holder_vals)})"
            else:
                return ", ".join(place_holder_vals)
            
        # PRIMARY KEYS
        if primary_keys and len(primary_keys[0]) > 0:
            # checking on the len of primary_keys[0]
            one_key = False if type[primary_keys[0]] in (tuple, list) else True
            pk_condition = "({}) IN ({})".format(
            # Column Names
            ", ".join(primary_keys[0] if not one_key else (primary_keys[0], )),

            # getting the primary key values     
            convert_tuples_format(primary_keys[1])
        )
            where_statement_all.append(pk_condition)

        # Additional WHERE
        if where_statement:
            where_statement_all.append(where_statement)

        # Combine
        conditions: str = (
            f"{join_statement} "
            f"{"WHERE " + " AND ".join(where_statement_all) if where_statement_all else ""} "
            f"{condition if condition else ""}" # Additional condition
        )

        if values:
             for v in values: combined_values.append(v)

        select_query = self.build_select_query(
            table,
            conditions,
            *columns
        )
        # returns list[dict[any]] | RepoError
        return await self.execute_read(
            select_query,
            *combined_values
        )
    async def get_info(self, model, table: str, primary_keys: dict, *columns: str) -> Model | RepoError:
        """
        Small help func, that builds an ORM for all major models
        
        :param model: Model that should get returned, needs to be a class itself, not an instance
        :model type: Model
        :param table: table where columns get selected from
        :table type: str
        :primary_keys: Primary Keys in example format -> {user_id: 12, community_id: 32}
        :primary_keys type: dict
        :columns: columns that should get returned
        :columns type: str
        :return: the specified model or RepoError
        :rtype: model | RepoError
        """
        # unpacking primary keys into where statement
        where_statement = ["{} = %s".format(k) for k, _ in primary_keys.items()]

        checked_val = self.check_pk_val(primary_keys)
        if checked_val != None: return checked_val # returns RepoError

        select_query = self.build_select_query(
            table,
            f"WHERE {" AND ".join(where_statement)}",
            *columns
        )
        # executing query
        info = await self.execute_read(select_query, *tuple(primary_keys.values()))
        if isinstance(info, self.RepoError): return info

        # defining model with the given sql return
        info_model: Model = self.create_model(info, model)
        return info_model # returning model or RepoError
    
    async def post_model(self, table: str, *models: Model, return_last_inserted_id: bool=False) -> None | BaseRepo.RepoError | int:
        """
        Given instances of the same model class, creates a db entry with the specified propertys from the user model\n
        Note: The models must have one primary key\n

        :param table: Table in which the model gets posted
        :type table: str
        :param model: Instances of the same model class
        :type model: Model
        :return: None or RepoError
        :rtype: None | RepoError
        """
        # Checking on Repo Error
        columns_values: tuple = self.get_columns_values(*models)
        if isinstance(columns_values, self.RepoError): return columns_values

        # calling functions to get sql query
        columns, values = columns_values
        if not columns or not values: return None # Nothing to insert

        insert_query, insert_val = self.build_insert_query(table, columns, values)

        # executing query
        if return_last_inserted_id:
            return await self.execute_write(insert_query, *insert_val, last_insert_id=True) # returns int | RepoError
        return await self.execute_write(insert_query, *insert_val)                          # returns None | RepoError

    def build_select_query(self, table: str, other_statement: str = "", *columns: str) -> str:
        """
        Builds a SQL Query with the given columns
        
        :param columns: Columns to select
        :colum type: str
        :param other_statement: statement for example where, join, limit..., default is ""
        :other_statement type: str
        :param table: selecting from that table
        :table type: str
        :return: SQL Query
        :rtype: str
        """

        # Building column statement
        selected_columns = ", ".join(columns) if columns else "*"

        # defining select_query
        select_query: str = f"SELECT {selected_columns} FROM {table} "

        # defining where statement
        select_query += f"{other_statement};"

        return select_query
    
    def build_insert_query(self, table: str, columns: list | GeneratorType, values: list[tuple]) -> tuple[str, list[any]]:
        """
        Builds a SQL-Insert-Query with the given columns and values
        
        :param table: table to insert the query
        :type table: str
        :param columns: columns where statement gets insertet
        :type columns: list
        :param values: values to insert, can be more than one, must be a list of tuples
        values will be replaced with %s to prevent injections and can be later replaced
        :type values: list[tuple]
        :return: tuple[SQL QUERY, list[Insert Values]] -> 
        :rtype: tuple[str, list[any]]
        """
        # first statement
        insert_query = f"INSERT INTO {table} "

        # add additional columns
        if columns: insert_query += f"({', '.join(columns)}) VALUES "

        # defining empty lists
        secure_values: list[str] = [] # outputs list[str]
        insert_val = []

        for i, section in enumerate(values):
            secure_values.append([])        # list where val get inserted

            for value in section:           # outputs secure_vals[i] to -> ['%s', '%s', '%s', '%s', '%s', '%s', '%s', 'DEFAULT']
                if value == "DEFAULT":
                    secure_values[i].append("DEFAULT")

                else:
                    secure_values[i].append("%s")
                    insert_val.append(value)

            # formatting section to '(%s, %s, %s, %s, %s, %s, %s, DEFAULT)'
            secure_values[i] = f'({", ".join(secure_values[i])})'

        # adding secure_values and end of query statement
        insert_query += ", ".join(secure_values) +";"

        # returning sql query + new val's to insert
        return insert_query, insert_val
    
    def build_update_query(self, table: str, update_val: dict, other_statement: str) -> tuple[str, list]:
        """
        Builds a sql update query with the given table, update values and where statement
        example -> build_update_query("users", {"user_name": "x", "user_email": "user@mail.com"}, "user_id = %s")

        :param table: table where statement gets executed
        :type table: str
        :param update_val: dictionary in format {parm: new_val, ...}
        :type update_val: dict
        :param other_statement: statemnt after set for example where, join...
        :other_statement type: str
        :return: SQL Query in format UPDATE {table} SET user_name = %s WHERE user_id = %s
        Will return a tuple of the SQL Query and a list with the values that can later replace the %s placeholders
        :rtype: tuple[str, list]
        """

        update_query: list = [f"UPDATE {table} SET"] # index = 1

        set_statement: list = []
        values: list = []

        for k, v in update_val.items():
            set_statement.append(f"{k} = %s")
            values.append(v)

        # adding set statement
        update_query.append(", ".join(set_statement))

        # adding where statement
        update_query.append(f"{other_statement};")
        return " ".join(update_query), values

    def build_delete_query(self, table: str, condition: str) -> str:
        """
        Builds a sql delete query with the given table and the last condition
        example -> build_delete_query("users", "WHERE user_id = 2")

        :param table: table where statement gets executed
        :type table: str
        :param condition: last condition for example, where, join, limit...
        :type condition: str
        :return: sql query
        :rtype: str
        """
        # for example DELETE FROM table_name WHERE condition;
        return f"DELETE FROM {table} {condition};"

    def create_model(self, sql_return: list, model: object) -> object | RepoError:
        """
        Unpacks the given list from the sql return and returns a Model or RepoError
        
        :param sql_return: the return from the sql select statement
        :type sql_return: list
        :param model: the class of the model that gets returned
        :type model: object
        :return: instance of the model class or RepoError
        :rtype: object | RepoError
        """

        # unpacking list
        if sql_return != []:
            sql_values: dict = sql_return[0]
            if type(sql_values) != dict:
                self.logger.warning(
                "Wrong type of sql_return, "
                "prefered type: dict, "
                f"given type: {type(sql_return)}"
            )
                return self.RepoError(
                    False,
                    5,
                    "Wrong type of sql_return",
                    SqlReturnTypeError(
                        "Wrong type of sql_return, "
                        "prefered type: dict, "
                        f"given type: {type(sql_return)}"
                    )
                )

        else:
            self.logger.info("Parsed an empty list!")

        # check if model is instance or class
        if not isinstance(model, type):
            self.logger.warning("Model is instance not class")
            return self.RepoError(
                False,
                3,
                "Model is instance not class",
                ModelError("Model is an instance of an class, not class itself")
            )
        
        # inspecting how many param the func takes
        len_call_signature = len(inspect.signature(model.__init__).parameters) - 1 # len of the param - self

        default_parm: list = [DEFAULT for _ in range(len_call_signature)]          # default value for not specified parm

        temp_model = model(*default_parm)                                          # initalising the model with the default parmeters

        # if return is [] -> return model with default parm
        if not sql_return: return temp_model

        # getting the attributes of temp_model
        for k, v in sql_values.items():

            temp_model_signature_parm = inspect.signature(temp_model.__init__).parameters
            if k in temp_model_signature_parm:

                # if the value of v has the same annotation as the model
                if type(v) in check_type(temp_model_signature_parm[k].annotation):
                    temp_model.__setattr__(k, v)                                    # setting attributes of model instance
                else:
                    self.logger.warning(f"Value '{k}'[{v}] hasn't the same annotation as specified in {model}")
                    return self.RepoError(
                        False,
                        3,
                        "Model-annotation Error",
                        ModelError(f"Value '{k}'[{v}] hasn't the same annotation as specified in {model}")
                    )
            else:
                self.logger.warning(f"Param {k} doesn't exist in {model}")
                return self.RepoError(
                    False,
                    3,
                    "Missing parm",
                    ModelError(f"Parameter {k} doesn't exist in {model}")
                )
            
        return temp_model

    def check_model_validity(self, *models) -> RepoError | object:
        """
        Checks if models are of the same instance and no class itself
        
        :param models: models to check
        :return: RepoError if *models is not valid else class from where all models inherit
        :rtype: RepoError | object
        """
        if not models:
            self.logger.warning("No model defined")
            return self.RepoError(
                False,
                3, "No model defined",
                ModelError("No model defined")
            )
        # definining model types
        model_types: set = {
            model.__class__
            if not isinstance(model, type)
            else TypeError
            for model in models
        }
        # checking if every model is instance of the same class
        if len(model_types) != 1 or TypeError in model_types:
            self.logger.warning("Every model in *models must be instance from the same class ")
            return self.RepoError(
                False,
                3,
                "Models must be instances of the same class",
                ModelError("Every model in *models must be instance from the same class ")
            )
        
        return model_types.pop()

    def get_columns_values(self, *models) -> tuple[GeneratorType, list] | RepoError:
        """
        Given user models, returns the models columns and values
        
        :param models: models (must be instances of the same class)
        :return: returns columns[GeneratorType] and values[list] or RepoError if an error ocurred
        :rtype: tuple[GeneratorType, list] | RepoError
        """
        base_class = self.check_model_validity(*models)
        if isinstance(base_class, self.RepoError): return base_class # returning RepoError
        
        # defining column
        model_parm = inspect.signature(base_class.__init__).parameters
        columns: GeneratorType = (model for model in model_parm if model != "self") # removing self
        
        # getting values from models
        values_items = []
        for model in models:
            # defining values
            attributes = (
                format_value(model.__getattribute__(parm)) # calling function with value of the parm
                for parm in model_parm
                if parm != "self"
            )
            values_items.append(tuple(attributes))
        return columns, values_items