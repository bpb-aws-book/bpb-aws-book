# pull official Amazon Linux 2023 base image
FROM amazonlinux:2023

# set work directory
WORKDIR /usr/src

#default port used by Django Web Applications
EXPOSE 8000

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy project
COPY inquisitive_bookworm_club /usr/src/inquisitive_bookworm_club
COPY setup.sh /usr/src/inquisitive_bookworm_club
COPY entrypoint.sh /usr/src/inquisitive_bookworm_club

# change working directory
WORKDIR /usr/src/inquisitive_bookworm_club

# remove pre existing virtual environment setup for the EC2 instance
RUN rm -rf env
RUN sh setup.sh

#install nginx
RUN dnf install nginx -y

#run gunicorn
CMD ["sh", "entrypoint.sh"]
