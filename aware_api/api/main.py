from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from datetime import datetime, timedelta

from aware_api import db
from aware_api.api import errors

app = FastAPI()
engine = db.connect_database("aware")
tables = db.all_tables(engine)


def df_to_json(df: pd.DataFrame, table: str) -> dict:
    columns = list(df.columns)
    ret = []
    for index, row in df.iterrows():
        data = []
        for col in columns:
            data.append(row[f"{col}"])
        dic = dict(zip(columns, data))
        ret.append(dic)
    return {"table": table, "result": ret}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/get_data")
def get_data(device_id: str = None, timestamp: str = None, emotion: str = None, _from: str = None, _to: str = None):
    queries = []
    target_tables = tables

    # デバイスIDがあればクエリに加える
    if device_id:
        device_id_query = f"device_id = '{device_id}'"
        queries.append(device_id_query)

    # タイムスタンプがあればクエリに加える
    if timestamp:
        if _to or _from:
            return errors.send_error(1, "timestamp")
        
        try:
            timestamp: datetime = datetime.strptime(timestamp, "%Y-%m-%d:%H")
        except ValueError:
            return errors.send_error(1, "timestampとfrom-toは両立できないよん")
        
        start_hour = (timestamp.hour // 3) * 3
        start_time = timestamp.replace(hour=start_hour)
        timestamp_query = f"timestamp = '{start_time}'"
        queries.append(timestamp_query)

    # 時間の範囲指定があればクエリに加える
    if _from or _to:
        if timestamp:
            return errors.send_error(1, "timestampとfrom-toは両立できないよん")
        
        if not _from or not _to:
            return errors.send_error(1, "_from, _to")
        
        try:
            _from = datetime.strptime(_from, "%Y-%m-%d:%H")
            _to = datetime.strptime(_to, "%Y-%m-%d:%H")
        except ValueError:
            return errors.send_error(1, "_from, _to")
        
        start_hour_from = (_from.hour // 3) * 3
        start_time_from = _from.replace(hour=start_hour_from)

        start_hour_to = (_to.hour // 3) * 3
        start_time_to = _to.replace(hour=start_hour_to)

        from_to_query = f"timestamp >= '{start_time_from}' and timestamp <= '{start_time_to}'"
        queries.append(from_to_query)
    
    # エモーションがあればクエリに加える(table)
    if emotion:
        if emotion not in tables:
            return errors.send_error(1, "emotion")
        target_tables = [emotion]

    # すべてのクエリを一つに
    all_query = f"where {' and '.join(queries)}"
    if not queries:
        all_query = ""

    res = []
    for table in target_tables:
        df = pd.read_sql(f"select * from {table} {all_query}", engine)
        res = res + [df_to_json(df, table)]
    return {"result": res}


@app.get("/get_today")
def get_today():
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    res = []
    for table in tables:
        df = pd.read_sql(f"select * from {table} where timestamp = '{today}'", engine)
        res = res + [df_to_json(df, table)]

    return {"result": res}



class SampleDTO(BaseModel):
    a: str

@app.post("/post")
async def sample_post(sample: SampleDTO):
    return sample
