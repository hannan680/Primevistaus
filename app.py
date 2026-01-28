from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import quote_plus
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

app = Flask(__name__)

# Database configuration - PostgreSQL
# Use environment variables for production, fallback to defaults for development
db_user = os.getenv('DB_USER', 'hannan')
db_password = os.getenv('DB_PASSWORD', 'DigitalProwler(3088)')
db_host = os.getenv('DB_HOST', '168.231.111.220')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'ipcheck')

# Check if full DATABASE_URL is provided (common in cloud platforms)
database_url = os.getenv('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # URL encode password if it contains special characters
    encoded_password = quote_plus(db_password)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model
class IPRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    country = db.Column(db.String(100))
    region = db.Column(db.String(100))
    city = db.Column(db.String(100))
    isp = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'isp': self.isp,
            'timestamp': self.timestamp.isoformat()
        }

# Create database tables
with app.app_context():
    db.create_all()

# IP Geolocation API endpoints (with fallbacks)
def get_user_ip():
    """Get the user's actual IP address"""
    # Check X-Forwarded-For header for real client IP (if behind proxy)
    x_forwarded_for = request.headers.get('X-Forwarded-For', '')
    if x_forwarded_for:
        # X-Forwarded-For may contain multiple IPs, take the first one
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.remote_addr
    return ip

def fetch_ip_data(ip_address=None):
    """Try multiple IP geolocation APIs with fallback
    If ip_address is provided, fetch data for that IP.
    Otherwise, fetch data for the requester's detected IP.
    """
    if not ip_address:
        ip_address = get_user_ip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # helper to format url
    def format_url(base, ip):
        if base == 'https://ipapi.co/':
            return f"{base}{ip}/json/"
        elif base == 'http://ip-api.com/':
            return f"{base}json/{ip}"
        elif base == 'https://ipinfo.io/':
            return f"{base}{ip}/json"
        return base
        
    api_configs = [
        {
            'base': 'https://ipapi.co/',
            'parser': lambda d: {
                'ip': d.get('ip', ip_address),
                'country': d.get('country_name', 'Unknown'),
                'region': d.get('region', 'Unknown'),
                'city': d.get('city', 'Unknown'),
                'isp': d.get('org', 'Unknown')
            }
        },
        {
            'base': 'http://ip-api.com/',
            'parser': lambda d: {
                'ip': d.get('query', ip_address),
                'country': d.get('country', 'Unknown'),
                'region': d.get('regionName', 'Unknown'),
                'city': d.get('city', 'Unknown'),
                'isp': d.get('isp', 'Unknown')
            }
        },
        {
            'base': 'https://ipinfo.io/',
            'parser': lambda d: {
                'ip': d.get('ip', ip_address),
                'country': d.get('country', 'Unknown'),
                'region': d.get('region', 'Unknown'),
                'city': d.get('city', 'Unknown'),
                'isp': d.get('org', 'Unknown')
            }
        }
    ]
    
    for api in api_configs:
        try:
            url = format_url(api['base'], ip_address)
            # Skip loopback/private IPs for public APIs as they will fail or return error
            if ip_address in ['127.0.0.1', 'localhost', '::1'] or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
                 print(f"Skipping public API for private IP: {ip_address}")
                 # For private IPs, return a dummy object so the UI doesn't crash
                 return {
                    'ip': ip_address,
                    'country': 'Local Network',
                    'region': 'Local',
                    'city': 'Local',
                    'isp': 'Local Network'
                 }

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Check if response contains error
                if 'error' in data or ('status' in data and data.get('status') == 'fail'):
                    continue
                parsed = api['parser'](data)
                print(f"Successfully fetched IP data for {ip_address} from {url}")
                return parsed
        except Exception as e:
            print(f"Error with {api['base']}: {e}")
            continue
    
    # Last resort: just return the IP
    return {
        'ip': ip_address,
        'country': 'Unknown',
        'region': 'Unknown',
        'city': 'Unknown',
        'isp': 'Unknown'
    }

@app.route('/')
def index():
    """Main page - fetches IP geolocation data"""
    ip_data = fetch_ip_data()
    
    if ip_data:
        ip_address = ip_data.get('ip', 'Unknown')
        
        # Check if IP already exists in database
        existing = IPRecord.query.filter_by(ip_address=ip_address).first()
        already_saved = existing is not None
        
        formatted_data = {
            'success': True,
            'ip': ip_address,
            'country': ip_data.get('country', 'Unknown'),
            'region': ip_data.get('region', 'Unknown'),
            'city': ip_data.get('city', 'Unknown'),
            'connection': {
                'isp': ip_data.get('isp', 'Unknown')
            },
            'already_saved': already_saved
        }
        return render_template('index.html', data=formatted_data)
    else:
        print("All IP geolocation APIs failed")
        return render_template('index.html', data={'success': False})

@app.route('/save-ip', methods=['POST'])
def save_ip():
    """Save IP address to database"""
    try:
        data = request.get_json()
        ip_address = data.get('ip')
        
        if not ip_address:
            return jsonify({
                'status': 'error',
                'message': 'IP address is required'
            }), 400
        
        # Fetch full IP details for the specific IP being saved
        ip_info = fetch_ip_data(ip_address)
        
        # Check if IP already exists
        existing = IPRecord.query.filter_by(ip_address=ip_address).first()
        
        if ip_info:
            if existing:
                # Update existing record
                existing.country = ip_info.get('country')
                existing.region = ip_info.get('region')
                existing.city = ip_info.get('city')
                existing.isp = ip_info.get('isp')
                existing.timestamp = datetime.utcnow()
                db.session.commit()
                return jsonify({
                    'status': 'success',
                    'message': f'IP {ip_address} updated successfully'
                })
            else:
                # Create new record
                new_record = IPRecord(
                    ip_address=ip_address,
                    country=ip_info.get('country'),
                    region=ip_info.get('region'),
                    city=ip_info.get('city'),
                    isp=ip_info.get('isp')
                )
                db.session.add(new_record)
                db.session.commit()
                return jsonify({
                    'status': 'success',
                    'message': f'IP {ip_address} saved successfully'
                })
        else:
            # Save with minimal data if API fails
            if existing:
                existing.timestamp = datetime.utcnow()
                db.session.commit()
                return jsonify({
                    'status': 'success',
                    'message': f'IP {ip_address} updated (limited details)'
                })
            else:
                new_record = IPRecord(ip_address=ip_address)
                db.session.add(new_record)
                db.session.commit()
                return jsonify({
                    'status': 'success',
                    'message': f'IP {ip_address} saved (API unavailable)'
                })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error saving IP: {str(e)}'
        }), 500

@app.route('/view-ips', methods=['GET'])
def view_ips():
    """View all saved IPs (optional admin endpoint)"""
    try:
        ips = IPRecord.query.order_by(IPRecord.timestamp.desc()).all()
        return jsonify({
            'status': 'success',
            'count': len(ips),
            'ips': [ip.to_dict() for ip in ips]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching IPs: {str(e)}'
        }), 500

@app.route('/test-api', methods=['GET'])
def test_api():
    """Test endpoint to check API connectivity"""
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Define APIs locally for testing
    verification_apis = [
        'https://ipapi.co/json/',
        'http://ip-api.com/json/',
        'https://ipinfo.io/json'
    ]
    
    for url in verification_apis:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            results.append({
                'url': url,
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'data': response.json() if response.status_code == 200 else None
            })
        except Exception as e:
            results.append({
                'url': url,
                'status_code': None,
                'success': False,
                'error': str(e)
            })
    
    return jsonify({
        'status': 'success',
        'results': results
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
