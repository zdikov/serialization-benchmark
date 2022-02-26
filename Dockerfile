FROM python:3.9

COPY . .

RUN pip install -r requirements.txt
RUN protoc --proto_path=. --python_out . benchmark.proto

ENTRYPOINT ["python3", "benchmark.py"]

