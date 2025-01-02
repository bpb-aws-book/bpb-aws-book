source env/bin/activate && \
gunicorn inquisitive_bookworm_club_project.wsgi:application --bind 0.0.0.0:8000
