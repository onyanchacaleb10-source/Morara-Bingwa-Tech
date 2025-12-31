# Quick Start - M-PESA STK Push

## 🚀 Ready to Deploy!

Your M-PESA STK Push service is fully configured. Choose your deployment method:

### Option 1: Docker Compose (Local Testing)
```bash
docker-compose up -d
# Visit http://localhost:5000/pay
```

### Option 2: Render (Free Cloud, 30 seconds)
1. Push to GitHub (already done ✅)
2. Go to https://render.com → Sign up
3. Create Web Service → Select your repo
4. Paste this as start command: 
   ```
   gunicorn -b 0.0.0.0:5000 app:app
   ```
5. Add 6 env vars (CONSUMER_KEY, CONSUMER_SECRET, PASSKEY, BUSINESS_SHORT_CODE, CALLBACK_URL, SANDBOX)
6. Deploy (5 mins)

### Option 3: Heroku (Classic)
```bash
heroku create
heroku config:set CONSUMER_KEY="your_key" ...
git push heroku main
heroku open
```

## 📋 What You Have

✅ Flask API with M-PESA integration  
✅ Docker containerization  
✅ GitHub Actions CI/CD  
✅ Environment configuration  
✅ API endpoints ready:
- `GET /pay` - Payment form
- `POST /api/pay` - Initiate STK push
- `POST /callback` - Receive callbacks

## 🔑 Required Credentials

Get from Safaricom M-PESA API:
- Consumer Key
- Consumer Secret  
- Lipa Na M-Pesa Passkey
- Till Number (Business Short Code)

## 📖 Documentation

- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed setup
- See [README.md](README.md) for API documentation
- Source: [app.py](app.py)

## 🧪 Test Locally

```bash
python app.py
# Then visit http://localhost:5000/pay
# Or test API:
curl -X POST http://localhost:5000/api/pay \
  -H "Content-Type: application/json" \
  -d '{"phone": "2547XXXXXXXX", "amount": "100"}'
```

## ⚡ Next Steps

1. Get Safaricom M-PESA API credentials
2. Update `.env` with your credentials
3. Choose deployment platform
4. Deploy (< 5 minutes)
5. Update CALLBACK_URL with deployed URL
6. Test payment flow

**Questions?** Check [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section.

Repository: https://github.com/onyanchacaleb10-source/Morara-Bingwa-Tech
