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

# change working directory
WORKDIR /usr/src/inquisitive_bookworm_club

# remove pre existing virtual environment setup for the EC2 instance
RUN rm -rf venv
#install dependencies
RUN dnf install pip -y
CMD ["sh", "setup.sh"]
RUN dnf install nginx -y

#run gunicorn
CMD ["python3", "-m", "venv", "env"]
CMD ["source", "env/bin/activate"]
CMD ["gunicorn", "inquisitive_bookworm_club_project.wsgi:application", "-b", "0.0.0.0:8000"]
