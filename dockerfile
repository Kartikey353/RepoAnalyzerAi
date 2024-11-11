FROM python:3.10.2-slim-bullseye  

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./requirements.txt .

RUN apt-get update -y && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

# Change directory to your Alembic directory
WORKDIR /code/app

# Run Alembic migrations from inside the Alembic directory
RUN alembic upgrade head

# Change back to your main application directory

# Start your application using Gunicorn


# Start the FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
