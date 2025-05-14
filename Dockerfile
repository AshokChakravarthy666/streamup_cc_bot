FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Make a writable volume for the session
VOLUME ["/app"]

# Expose port if needed
EXPOSE 8080

# Run your bot
CMD ["python", "main.py"]
