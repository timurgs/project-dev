FROM python:3.9
COPY . /app
ENV PYTHONPATH=/app
RUN pip install -r /app/requirements.txt
CMD gunicorn app.stocks_products.wsgi -b 0.0.0.0:8000
