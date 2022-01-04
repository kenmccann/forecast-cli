FROM python:3.9.1-alpine3.12

ADD forecast-cli.py /
RUN pip install requests

ENTRYPOINT ["python", "-u", "/forecast-cli.py"]