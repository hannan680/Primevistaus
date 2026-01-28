# IP Detection Application

A Flask web application that detects and saves IP address geolocation information to a database.

## Features

- Automatic IP geolocation detection
- Display IP address, country, region, city, and ISP
- Save IP information to SQLite database
- View all saved IPs via API endpoint

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## API Endpoints

- `GET /` - Main page with IP detection
- `POST /save-ip` - Save IP address to database
- `GET /view-ips` - View all saved IP addresses (JSON)

## Database

The application uses SQLite database (`ip_detection.db`) to store IP records with the following fields:
- IP Address
- Country
- Region
- City
- ISP
- Timestamp

## Requirements

- Python 3.7+
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- requests 2.31.0
# Primevistaus
