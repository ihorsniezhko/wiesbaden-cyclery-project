# 🚀 Production Deployment

## Prerequisites
- Heroku account
- Stripe account
- Gmail account
- AWS account (optional, for images)

## Quick Deploy

### 1. Create Heroku App
```bash
heroku create wiesbaden-cyclery-project
```

### 2. Configure Environment
```bash
# Django
heroku config:set DEBUG=False
heroku config:set SECRET_KEY="your-secret-key"

# Database (Code Institute PostgreSQL)
heroku config:set DATABASE_URL="postgresql://..."

# Stripe
heroku config:set STRIPE_PUBLIC_KEY="pk_live_..."
heroku config:set STRIPE_SECRET_KEY="sk_live_..."
heroku config:set STRIPE_WH_SECRET="whsec_..."

# Email (Gmail)
heroku config:set EMAIL_HOST_USER="your-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="your-app-password"

# AWS S3 (optional)
heroku config:set USE_AWS=True
heroku config:set AWS_ACCESS_KEY_ID="..."
heroku config:set AWS_SECRET_ACCESS_KEY="..."
heroku config:set AWS_STORAGE_BUCKET_NAME="..."
```

### 3. Deploy
```bash
git push heroku master
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku run python manage.py loaddata products/fixtures/categories.json
heroku run python manage.py loaddata products/fixtures/sizes.json
heroku run python manage.py loaddata products/fixtures/products.json
```

## External Services Setup

### Stripe
1. Get API keys from https://dashboard.stripe.com/apikeys
2. Create webhook: `https://your-app.herokuapp.com/orders/webhook/stripe/`
3. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`

### Gmail SMTP
1. Enable 2-Factor Authentication
2. Create App Password: Google Account → Security → App passwords
3. Use 16-character password as `EMAIL_HOST_PASSWORD`

### AWS S3 (Optional)
1. Create S3 bucket in `eu-central-1`
2. Create IAM user with S3 read/write access
3. Configure bucket policy for public read and authenticated write access

## Verification Checklist
- [ ] Site loads at Heroku URL
- [ ] Products display with images
- [ ] Can add items to cart
- [ ] Stripe payment form works
- [ ] Test payment: `4242 4242 4242 4242`
- [ ] Order confirmation email received
- [ ] Admin panel accessible

## Monitoring
```bash
heroku logs --tail    # View logs
heroku ps             # Check status
heroku restart        # Restart app
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Static files 404 | `heroku run python manage.py collectstatic` |
| Database error | Check `DATABASE_URL` config |
| Payment fails | Verify Stripe live keys |
| No emails | Check Gmail app password |
| Images broken | Verify AWS credentials |

---

**Live Site**: https://wiesbaden-cyclery-project-818faeff3e83.herokuapp.com
