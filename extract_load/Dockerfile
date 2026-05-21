FROM python:slim

COPY . /extract_load/

WORKDIR /extract_load

RUN pip install -r requirements.txt

CMD ["python","main.py"]