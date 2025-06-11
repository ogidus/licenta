import subprocess
import socket
import requests
import sys

# ============ CONFIGURATION ============

# Services to check (local)
LOCAL_SERVICES = ['mysqld', 'semaphore', 'grafana-server']

# Remote PostgreSQL server details
POSTGRESQL_HOST = '192.168.1.137'  # Change this
POSTGRESQL_PORT = 30200  # Default PostgreSQL port

# Telegram Bot config
TELEGRAM_BOT_TOKEN = '6811108044:AAGtvRNxz4YiTQPHOme5SswRO1dxodIoO9Q'
TELEGRAM_CHAT_ID = '670248004'

# ============ FUNCTIONS ============

def check_service_status(service_name):
    """Check if a local service is active using systemctl."""
    try:
        result = subprocess.run(['systemctl', 'is-active', service_name],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        status = result.stdout.strip()
        return status == 'active'
    except Exception as e:
        print(f"Error checking service {service_name}: {e}")
        return False

def check_postgresql_connection(host, port, timeout=5):
    """Check remote PostgreSQL server accessibility."""
    try:
        with socket.create_connection((host, port), timeout):
            return True
    except Exception as e:
        print(f"PostgreSQL connection error: {e}")
        return False

def send_telegram_notification(message):
    """Send notification via Telegram bot."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Telegram notification error: {e}")

def main():
    errors = []

    # Check local services
    for service in LOCAL_SERVICES:
        if not check_service_status(service):
            error_msg = f"Service '{service}' is NOT running!"
            print(error_msg)
            errors.append(error_msg)

    # Check remote PostgreSQL
    if not check_postgresql_connection(POSTGRESQL_HOST, POSTGRESQL_PORT):
        error_msg = f"Cannot connect to PostgreSQL at {POSTGRESQL_HOST}:{POSTGRESQL_PORT}!"
        print(error_msg)
        errors.append(error_msg)

    # Send Telegram notification if any errors
    if errors:
        notification_message = "⚠️ Platform Validation Alert:\n" + "\n".join(errors)
        send_telegram_notification(notification_message)
    else:
        print("All services are running and PostgreSQL is reachable.")

if __name__ == "__main__":
    main()
