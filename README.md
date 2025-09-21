# 🚴‍♂️ Wiesbaden Cyclery - E-commerce Platform

[![Django](https://img.shields.io/badge/Django-3.2.25-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-4.6.2-purple.svg)](https://getbootstrap.com/)

A comprehensive Django-based e-commerce platform for a bicycle shop, featuring modern payment processing, user authentication, product management, and responsive design.

## 🎯 Project Overview

Wiesbaden Cyclery is a **full-featured e-commerce platform** built with Django 3.2.25, designed specifically for bicycle shops. The platform provides a complete online shopping experience with secure payment processing, user account management, product catalog, and comprehensive administrative tools.

### 🌟 Key Features (In Development)

- **🛍️ E-commerce Core**: Product catalog ✅, shopping cart, secure checkout
- **👤 User Management**: Registration, authentication, user profiles ✅
- **💳 Payment Processing**: Stripe integration with EUR currency support
- **📱 Responsive Design**: Bootstrap 4 with mobile-first approach
- **🔒 Security**: GDPR compliant with comprehensive security measures
- **☁️ Cloud Integration**: AWS S3 for media, Gmail SMTP for emails

## 🛠️ Technology Stack

### Backend
- **Django 3.2.25** (LTS) - Web framework
- **Python 3.11** - Programming language
- **SQLite** - Development database
- **PostgreSQL** - Production database (Code Institute)

### Frontend
- **Bootstrap 4.6.2** - CSS framework
- **Font Awesome 4.7.0** - Icons
- **jQuery 3.5.1** - JavaScript library
- **Google Fonts (Roboto Serif)** - Typography

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd wiesbaden_cyclery_project
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment configuration**
Copy `.env.example` to `.env` and configure your settings:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here

# For production with Code Institute PostgreSQL:
# CI_DATABASE_URL=postgresql://neondb_owner:npg_L95rzFapgvun@ep-morning-art-a2n0h2k6.eu-central-1.aws.neon.tech/quail_plus_crust_122150
```

4. **Database setup**
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. **Run development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 📊 Development Progress

This project is being developed in stages to demonstrate realistic e-commerce development:

- ✅ **Stage 1**: Project Foundation - Basic Django setup and homepage
- ✅ **Stage 2**: User Authentication - Registration and login system
- ✅ **Stage 3**: Product Catalog - Product management and display
- ⏳ **Stage 4**: Shopping Cart - Cart functionality and calculations
- ⏳ **Stage 5**: Order Processing - Checkout and order management
- ⏳ **Stage 6**: Payment Integration - Stripe payment processing
- ⏳ **Stage 7**: Email System - Order confirmations and notifications
- ⏳ **Stage 8**: Enhanced Features - Advanced functionality
- ⏳ **Stage 9**: Testing Suite - Comprehensive testing
- ⏳ **Stage 10**: Production Deployment - Heroku deployment

## 🧪 Testing

```bash
# Run Django tests
python manage.py test

# Check for issues
python manage.py check
```

## 📚 Documentation

- **Setup Guide**: See installation instructions above
- **Development**: Follow the staged development approach
- **Contributing**: Follow Django best practices and PEP 8

## 🔧 Development

This project follows professional Django development practices:

- **Clean Code**: PEP 8 compliant with comprehensive documentation
- **Testing**: Comprehensive test coverage for all functionality
- **Security**: CSRF protection, XSS prevention, secure authentication
- **Performance**: Optimized database queries and static file handling

## 📝 License

This project is developed for educational and demonstration purposes.

---

**Note**: This is an active development project. Features are being added incrementally following professional development practices.