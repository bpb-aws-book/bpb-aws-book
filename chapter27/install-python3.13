# Install development tools and dependencies
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y openssl-devel bzip2-devel libffi-devel zlib-devel

# Download Python 3.13
cd /tmp
wget https://www.python.org/ftp/python/3.13.0/Python-3.13.0.tgz
tar xzf Python-3.13.0.tgz
cd Python-3.13.0

# Configure with altinstall to avoid overwriting system Python
./configure --enable-optimizations --prefix=/usr/local
make -j $(nproc)
sudo make altinstall

# Verify installation
python3.13 --version

# Create virtual environment with Python 3.13
python3.13 -m venv /path/to/myenv
source /path/to/myenv/bin/activate

#remove tmp dir
sudo rm -rf /tmp/Python-3.13.0*
