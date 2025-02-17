python3 -m venv env && \
source env/bin/activate && \
python3 -m pip install --upgrade pip && \
pip install -r requirements.txt && \
dnf install -y postgresql15 postgresql15-contrib && \
chmod -R a+rwx env && \
deactivate
