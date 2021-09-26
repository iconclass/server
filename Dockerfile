FROM iconclass_base

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src /data

CMD exec uvicorn --host 0.0.0.0 --port $PORT --workers 1 app:app
