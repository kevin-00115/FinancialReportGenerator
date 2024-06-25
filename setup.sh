# setup.sh
#!/bin/sh
# Update the system
apt-get update
# Install Google Chrome along with necessary fonts and dependencies
apt-get install -y google-chrome-stable
# Run your main Python script
python3 main.py