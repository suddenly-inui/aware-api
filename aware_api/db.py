import pandas as pd
from sqlalchemy import create_engine, text

from aware_api import constants


def connect_database(database: str):
    url = f'mysql+pymysql://{constants.MYSQL_USER}:{constants.MYSQL_PASSWORD}@{constants.MYSQL_HOST}:{constants.MYSQL_PORT}/{database}?charset=utf8'
    engine = create_engine(url, echo=False)
    return engine


def execute_sql(engine, sql):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        conn.commit()
    return result

def insert_data(engine, table: str, data: dict):
    keys = list(data.keys())
    values = list(data.values())
    sql = f"INSERT INTO {table}({','.join(keys)}) VALUES ({','.join(values)})"
    execute_sql(engine, sql)


def reset_table(engine, table):
    if type(table) == str:
        table = [table]

    with engine.connect() as conn:
        for t in table:
            execute_sql(engine, f"drop table if exists {t}")
            execute_sql(engine, f"create table {t} (id INT PRIMARY KEY AUTO_INCREMENT NOT NULL, device_id VARCHAR(64), label INT, timestamp datetime(2))")


def all_tables(engine):
    r = execute_sql(engine, "show tables;")
    tables = []
    for i in r:
        for j in i:
            tables.append(j)
    return tables

def create_mock(engine, table):
    reset_table(engine, table)
    data = lambda device_id, label, datetime: {"device_id": device_id, "label": label,"timestamp": datetime}
    datas = [
        data("'aaaaa'", "0", "'2020-1-1 9:00:00'"),
        data("'aaaaa'", "0", "'2020-1-1 12:00:00'"),
        data("'aaaaa'", "1", "'2020-1-1 15:00:00'"),
        data("'aaaaa'", "1", "'2020-1-1 18:00:00'"),
        data("'aaaaa'", "-1", "'2020-1-1 21:00:00'"),
        data("'aaaaa'", "-1", "'2020-1-1 0:00:00'"),
        data("'bbbbb'", "0", "'2020-1-1 9:00:00'"),
        data("'bbbbb'", "0", "'2020-1-1 12:00:00'"),
        data("'bbbbb'", "1", "'2020-1-1 15:00:00'"),
        data("'bbbbb'", "1", "'2020-1-1 18:00:00'"),
        data("'bbbbb'", "-1", "'2020-1-1 21:00:00'"),
        data("'bbbbb'", "-1", "'2020-1-1 0:00:00'"),
        data("'ccccc'", "0", "'2020-1-1 9:00:00'"),
        data("'ccccc'", "0", "'2020-1-1 12:00:00'"),
        data("'ccccc'", "1", "'2020-1-1 15:00:00'"),
        data("'ccccc'", "1", "'2020-1-1 18:00:00'"),
        data("'ccccc'", "-1", "'2020-1-1 21:00:00'"),
        data("'ccccc'", "-1", "'2020-1-1 0:00:00'"),
    ]
    for d in datas:
        for t in table:
            insert_data(engine, t, d)

if __name__ == "__main__":
    engine = connect_database("aware")
    create_mock(engine, ["emotion1", "emotion2", "emotion3"])
    all_tables(engine)


# query = "select * from emotion1"
# df = pd.read_sql(query, con=engine)
# print(df)
