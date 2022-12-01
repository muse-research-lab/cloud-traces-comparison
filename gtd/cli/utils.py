from sqlalchemy import create_engine


def create_mysql_con(  # type: ignore
    host: str, port: int, username: str, passw: str, database: str
):
    db_string = (
        f"mysql+mysqlconnector://{username}:{passw}@{host}:{port}/{database}"
    )
    db = create_engine(db_string)
    return db.connect()
