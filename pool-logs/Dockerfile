#####################
# FINAL ENVIRONMENT #
#####################

FROM python:3.13-alpine

WORKDIR /app

COPY src/requirements.txt .
COPY src/app.py .

RUN pip install \
    --no-cache-dir \
    -r requirements.txt

CMD ["python", "app.py"]
