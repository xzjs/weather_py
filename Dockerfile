FROM python:2
ADD . /app
WORKDIR /app
RUN chmod -R 777 /app
RUN pip install -r requirements.txt
CMD ["python", "weather.py"]