FROM python:3.10-slim-buster
EXPOSE 80

# Environment variables

## Database
ENV DB_HOST=undefined
ENV DB_NAME=undefined
ENV DB_PASSWORD=undefined
ENV DB_PORT=undefined
ENV DB_USER=undefined

## Mail
ENV EMAIL_ENVIRONMENT=sendgrid
ENV SENDGRID_FROM_EMAIL=mail@petconnect.com
ENV SENDGRID_API_KEY=undefined

## Crypto
ENV TOKEN_SECRET=undefined

## Mercadopago
ENV ACCESS_TOKEN=undefined

## URLS
ENV BE_URL=undefined
ENV FE_URL=undefined

## S3
ENV S3_AWS_ACCESS_KEY=undefined
ENV S3_AWS_ACCESS_SECRET=undefined
ENV S3_BUCKET_NAME=undefined

# Install dependencies

RUN apt-get update
ADD requirements.txt ./
RUN pip install --ignore-installed -r requirements.txt
COPY . /code/
WORKDIR /code

# Start server

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80", "--root-path", "/"]
