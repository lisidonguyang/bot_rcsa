# Use Python 3.9+ as the base image
FROM selenium

# Set working directory
WORKDIR /app



# Create browsers directory and install Firefox
#RUN mkdir /browsers && \
#    curl -L https://ftp.mozilla.org/pub/firefox/releases/108.0/linux-x86_64/en-US/firefox-108.0.tar.bz2 -o /browsers/firefox-108.0.tar.bz2 && \
#    tar xjf /browsers/firefox-108.0.tar.bz2 -C /browsers && \
#    rm /browsers/firefox-108.0.tar.bz2

# Add Firefox to PATH
#ENV PATH="/browsers/firefox:${PATH}"

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directory for the database
RUN mkdir -p /app/data

# Set environment variable for the database location
ENV DB_PATH=/app/data/file.db

# Create volume for persistent storage
VOLUME /app/data

# Run the script
CMD ["python", "main.py"]