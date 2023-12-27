
class DatabaseError(Exception):
    pass

class NotFoundError(DatabaseError):
    pass

class UniqueValueError(DatabaseError):
    pass