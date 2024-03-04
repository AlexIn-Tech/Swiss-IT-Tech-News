# Use an Alpine Linux image with Python 3 installed
FROM python:3.12.2-alpine3.19

# Set the working directory in the container
WORKDIR /app

# Copy the requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the bot script and configuration file into the container
COPY bot/telegram_rss_bot.py /app/

# Use dotenv library to load environment variables at runtime
CMD ["sh", "-c", "python telegram_rss_bot.py"]
