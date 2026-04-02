class ExistingAttributeError(Exception):
    """Raised when a value in the db already exists"""

class QuerySyntaxError(Exception):
    """Raised when the syntax of the sql query has an error"""

class ModelError(Exception):
    """Raised when a non-valid Model gets parsed in a function parameter"""

class SqlReturnTypeError(Exception):
    """Raised when something is wrong with the sql-return-type"""