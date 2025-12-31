# Deployment Guide - M-PESA STK Push Service

## 1. Local Testing (Docker Compose)

```bash
cd /workspaces/Morara-Bingwa-Tech
docker-compose up -d
```

Then visit: http://localhost:5000/pay

## 2. Render Deployment (Free)

1. Go to https://render.com
2. Create account & connect GitHub
3. New → Web Service
4. Select this repository
5. Configure:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn -b 0.0.0.0:5000 app:app`
6. Add Environment Variables:
   - CONSUMER_KEY
   - CONSUMER_SECRET
   - PASSKEY
   - BUSINESS_SHORT_CODE
   - CALLBACK_URL (must be HTTPS)
   - SANDBOX=true
7. Deploy

## 3. Heroku Deployment

```bash
heroku login
heroku create morara-bingwa-mpesa
heroku config:set CONSUMER_KEY="xxx" CONSUMER_SECRET="xxx" PASSKEY="xxx"
heroku config:set BUSINESS_SHORT_CODE="7818012" CALLBACK_URL="https://your-app.herokuapp.com/callback"
git push heroku main
heroku logs --tail
```

## 4. Docker Registry (AWS ECR, Docker Hub, GCR)

```bash
# Build & tag
docker build -t your-registry/morara-bingwa-stk:latest .

# Push
docker push your-registry/morara-bingwa-stk:latest

# Run
docker run -p 5000:5000 \
  -e CONSUMER_KEY="xxx" \
  -e CONSUMER_SECRET="xxx" \
  -e PASSKEY="xxx" \
  -e CALLBACK_URL="https://yourdomain.com/callback" \
  your-registry/morara-bingwa-stk:latest
```

## 5. Update Callback URL

After deployment, get your public URL and update:
- `.env` file: `CALLBACK_URL=https://your-deployed-url.com/callback`
- Safaricom dashboard: Configure callback URL for your till

## Testing Your Deployment

```bash
# Get your deployed URL (e.g., https://morara-bingwa.onrender.com)

# Test payment form
curl https://morara-bingwa.onrender.com/pay

# Test API
curl -X POST https://morara-bingwa.onrender.com/api/pay \
  -H "Content-Type: application/json" \
  -d '{"phone": "2547XXXXXXXX", "amount": "100"}'
```

## Environment Variables Checklist

- [ ] CONSUMER_KEY (from Safaricom)
- [ ] CONSUMER_SECRET (from Safaricom)
- [ ] PASSKEY (Lipa Na M-Pesa passkey)
- [ ] BUSINESS_SHORT_CODE (your till number)
- [ ] CALLBACK_URL (public HTTPS URL)
- [ ] SANDBOX (true for testing, false for production)

## Common Issues

**"Failed to get access token"**
- Verify CONSUMER_KEY and CONSUMER_SECRET are correct
- Ensure they're from the correct Safaricom sandbox/production environment

**"STK push failed"**
- Check CALLBACK_URL is publicly accessible and HTTPS
- Verify phone number format (2547XXXXXXXX)
- Confirm BUSINESS_SHORT_CODE matches your till

**"Invalid passkey"**
- Verify PASSKEY matches Safaricom dashboard
- Check BUSINESS_SHORT_CODE is correct

## Next Steps

1. Configure Safaricom credentials in your deployment platform
2. Update CALLBACK_URL with your deployed application URL
3. Test the `/pay` endpoint in your browser
4. Monitor logs for any errors
5. Integrate with your main application

## Support

Safaricom API Documentation: https://developer.safaricom.co.ke
