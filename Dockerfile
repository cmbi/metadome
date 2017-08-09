FROM python:3.5

# dependencies

# metadom-api
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt
COPY metadom_api/. /usr/src/app

CMD ["python", "application.py"]
