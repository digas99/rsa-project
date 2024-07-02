FROM python:3.10

RUN apt-get update \
	&& apt-get install -y --no-install-recommends 

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

CMD ["python3", "dashboard/dashboard.py"]