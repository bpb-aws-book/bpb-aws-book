python3 -m venv env && \
source env/bin/activate && \
python3 -m pip install --upgrade pip && \
python3 -m pip install django && \
python3 -m pip install gunicorn && \
python3 -m pip install boto3 psycopg2-binary aws-secretsmanager-caching && \
dnf install -y postgresql15 postgresql15-contrib && \
chmod -R a+rwx env && \
deactivate
