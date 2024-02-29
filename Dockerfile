# Use an Alpine Linux image with Python 3 installed
FROM python:3.12-alpine

# Set the working directory in the container
WORKDIR /app

# Install dependencies needed for compiling certain Python packages, if necessary
RUN apk add --no-cache build-base libxml2-dev libxslt-dev

# Copy the requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script and configuration file into the container
COPY bot/telegram_rss_bot.py /app/

# Use dotenv library to load environment variables at runtime
CMD ["sh", "-c", "python telegram_rss_bot.py"]
