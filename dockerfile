FROM python:3.11

RUN apt update
RUN apt install -y python3-pip python3-dev build-essential
# copy the python script
COPY . .
COPY main.py /opt/main.py 
# Install python dependencies
COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt 
# Create directory for the database
RUN mkdir -p /app/data

# Set environment variable for the database location
ENV DB_PATH=/app/data/file.db

# Create volume for persistent storage
VOLUME /app/data




# Copy the rest of the application
COPY . .

USER root
# Run the script
CMD ["python3", "main.py"]