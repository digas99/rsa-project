FROM python:3.10

RUN apt-get update \
	&& apt-get install -y --no-install-recommends

WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY src/groundstation /app/

CMD ["python3", "dashboard/dashboard.py"]