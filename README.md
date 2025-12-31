# Morara Bingwa - M-PESA STK Push Service

A Flask-based service for initiating M-PESA STK Push payments via Safaricom's API.

## Features
- STK Push Initiation
- Token Caching
- Phone Validation
- Error Handling
- Callback Support
- Docker Ready

## Quick Start

```bash
docker-compose up -d
```

## Local Setup
```bash
pip install -r requirements.txt
python app.py
```

## Configuration
```
CONSUMER_KEY=your_key
CONSUMER_SECRET=your_secret
PASSKEY=your_passkey
BUSINESS_SHORT_CODE=7818012
CALLBACK_URL=https://yourdomain.com/callback
SANDBOX=true
```

## API Endpoints

**Payment Form:** `GET /pay?amount=200`

**Initiate STK Push:**
```
POST /api/pay
{
  "phone": "2547XXXXXXXX",
  "amount": "200"
}
```

**Callback Endpoint:** `POST /callback`

## Deployment Options

### Docker
```bash
docker build -t morara-bingwa-stk .
docker run -p 5000:5000 --env-file .env morara-bingwa-stk
```

### Cloud Platforms
- Render: Connect GitHub repo, set env vars
- Heroku: `git push heroku main`
- AWS/GCP/Azure: Push Docker image

## Phone Formats Supported
- 07XXXXXXXX (Kenya local)
- 7XXXXXXXX (auto-prefix 254)
- 2547XXXXXXXX (full international)
- +2547XXXXXXXX (with +)

## Data Packages (Purchase Once Daily)
SMS Packages (Purchase Multiple Times Daily)
Special & Minutes Offers
