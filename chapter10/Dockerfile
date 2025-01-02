# pull official Amazon Linux 2023 base image
FROM amazonlinux:2023

# set work directory
WORKDIR /usr/src

#default port used by Django Web Applications
EXPOSE 8000

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
#RUN python3 -m venv env && source env/bin/activate && python3 -m pip install --upgrade pip && \
#python3 -m pip install django gunicorn && \
#python3 -m pip install boto3 psycopg2-binary aws-secretsmanager-caching && \
#dnf install -y postgresql15 postgresql15-contrib && \
#chmod -R a+rwx env && deactivate && \
#dnf install nginx -y

# copy project
COPY inquisitive_bookworm_club /usr/src/inquisitive_bookworm_club

# change working directory
WORKDIR /usr/src/inquisitive_bookworm_club

# remove pre existing virtual environment
RUN rm -rf venv

RUN sh setup.sh

RUN dnf install nginx -y

python3 -m venv env && \
source env/bin/activate && \

CMD ["python3", "-m", "venv", "env"]
CMD ["source", "env/bin/activate"]
CMD ["gunicorn", "inquisitive_bookworm_club_project.wsgi:application", "-b", "0.0.0.0:8000"]
