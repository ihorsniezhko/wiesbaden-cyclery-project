# 🚴‍♂️ Wiesbaden Cyclery - E-commerce Platform

[![Django](https://img.shields.io/badge/Django-3.2.25-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-4.6.2-purple.svg)](https://getbootstrap.com/)

A comprehensive Django-based e-commerce platform for a bicycle shop, featuring modern payment processing, user authentication, product management, and responsive design.

## 🎯 Project Overview

Wiesbaden Cyclery is a **full-featured e-commerce platform** built with Django 3.2.25, designed specifically for bicycle shops. The platform provides a complete online shopping experience with secure payment processing, user account management, product catalog, and comprehensive administrative tools.

### 🌟 Key Features

- **🛍️ E-commerce Core**: Product catalog ✅, shopping cart ✅, secure checkout ✅, stock tracking ✅
- **👤 User Management**: Registration, authentication, user profiles ✅
- **💳 Payment Processing**: Stripe integration with EUR currency support ✅
- **📧 Email System**: Order confirmations and status updates with Gmail SMTP ✅
- **📬 Newsletter**: Mailchimp integration with GDPR-compliant signup ✅
- **🔍 Order Tracking**: Customer self-service order status tracking ✅
- **🔒 Legal Compliance**: Privacy Policy, Terms of Service, GDPR cookie consent ✅
- **⭐ Product Reviews**: Customer review system with ratings ✅
- **🔍 SEO Optimization**: Meta tags, XML sitemaps, structured data, social sharing ✅
- **📱 Responsive Design**: Bootstrap 4 with mobile-first approach ✅
- **🌐 Social Media**: Facebook Business page integration ✅
- **☁️ Cloud Ready**: Prepared for AWS S3 and production deployment

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
# CI_DATABASE_URL=your_code_institute_database_url_here
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

## 🛒 Product Catalog

### Current Inventory (18 Products)
- **🚴 Road Bikes** (2): Trek Domane AL 2, Specialized Allez Elite
- **🏔️ Mountain Bikes** (2): Giant Talon 1, Trek Fuel EX 5
- **⚡ Electric Bikes** (1): Bosch Performance E-Bike
- **🧰 Accessories** (6): Helmet, Gloves, Lock, Water Bottle, Lights, Pump
- **🔧 Components** (4): Shimano Chain, Professional Wheel, Premium Tire, Handlebar Grips
- **🏷️ Sale Items** (3): Discounted Helmet, Clearance Gloves, Special Offer Chain

### Size Standardization
- **Bicycles & Accessories**: S, M, L, XL sizes only
- **Components**: No size variations (universal fit)
- **Professional Images**: High-quality Unsplash photography for all products

## 📊 Development Progress

This project is being developed in stages to demonstrate realistic e-commerce development:

- ✅ **Stage 1**: Project Foundation - Basic Django setup and homepage
- ✅ **Stage 2**: User Authentication - Registration and login system
- ✅ **Stage 3**: Product Catalog - Product management and display
- ✅ **Stage 4**: Shopping Cart - Cart functionality and calculations
- ✅ **Stage 5**: Order Processing - Checkout and order management
- ✅ **Stage 6**: Payment Integration - Stripe payment processing
- ✅ **Stage 7**: Email System - Gmail SMTP integration and Mailchimp newsletter
- ✅ **Stage 8**: Legal Compliance - Privacy Policy, Terms of Service, GDPR cookie consent
- ✅ **Stage 9**: Enhanced Features - Product reviews, context-aware logic, performance optimizations
- ⏳ **Stage 10**: Testing Suite - Comprehensive testing (66+ automated tests)
- ✅ **Stage 11**: SEO Optimization - Meta tags, sitemaps, structured data, social media integration
- ✅ **Stage 12**: Stock Tracking System - Comprehensive inventory management with overselling prevention

## 📝 Development Notes

### Naming Convention Evolution

**Note**: During early development, some commit messages and documentation used "Task X" instead of "Stage X" naming convention. This inconsistency exists in the Git history for the following:

- **Commit Messages**: Some commits for Stage 6 (Stripe Payment Integration) use "Task 6" in commit messages
- **GitHub Issues**: All issues have been standardized to use "Stage X" naming
- **Documentation**: All current documentation uses "Stage X" naming

**Going Forward**: All future commits, issues, and documentation will consistently use the "Stage X" naming convention. This demonstrates a real-world scenario where naming conventions evolve during project development, and Git history preservation takes precedence over perfect consistency.

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

## 🎨 Image Attribution & Copyright

### Product Images
All product images are sourced from **Unsplash** under the Unsplash License (free for commercial use):

#### Professional Photography Credits:
- **Road Bikes**: Photos by Sies Kranen, Tasha Kostyuk
- **Mountain Bikes**: Photos by Dick Honing, Michał Robak  
- **Electric Bikes**: Photo by Mukkpetebike
- **Accessories**: Photos by Kaffeebart, MESTO Sprayers, Daiki Sato, Suraj Tomer, Egor Komarov, Sidral Mundet
- **Components**: Photos by Wayne Bishop, Yomex Owo, yasara hansani, Kelly Common
- **Hero Background**: Photo by Meg Jenson

**Complete Attribution**: See `media/UNSPLASH_ATTRIBUTIONS.md` for detailed photographer credits.

### License Information
- **Unsplash License**: All images are free to use for any purpose, including commercial use
- **Attribution**: Provided as courtesy to photographers
- **Quality**: Professional photography optimized for web display (800x600px)

## 🚀 Advanced Features (Stage 9 & 11)

### Stage 9: Enhanced Features ✅
- **Product Review System**: Customer ratings and reviews with moderation
- **Context-Aware Logic**: Intelligent product management with size-aware behavior
- **Performance Optimizations**: Database query optimization, template caching
- **Enhanced Admin Interface**: Improved product management with bulk operations

### Stage 11: SEO Optimization ✅
- **Dynamic Meta Tags**: Page-specific titles, descriptions, and keywords
- **XML Sitemaps**: Automated sitemaps for products, categories, and static pages
- **Structured Data**: JSON-LD schema markup for business and product information
- **Social Media Integration**: Open Graph and Twitter Card tags for rich previews
- **Search Engine Tools**: Robots.txt, canonical URLs, SEO testing page

### Stage 12: Stock Tracking System ✅
- **Smart Stock Validation**: Prevents overselling with real-time stock checking
- **Cart-Aware Inventory**: Considers items already in user's cart when calculating availability
- **Dynamic Stock Display**: Shows available quantities and cart status on product pages
- **Frontend Validation**: JavaScript controls respect stock limits with visual feedback
- **Backend Protection**: Server-side validation prevents overselling even if frontend is bypassed
- **Order Integration**: Stock automatically decremented on successful purchases
- **User-Friendly Messaging**: Clear stock warnings and availability information

## 🔧 Development

This project follows professional Django development practices:

- **Clean Code**: PEP 8 compliant with comprehensive documentation
- **Testing**: Comprehensive test coverage for all functionality
- **Security**: CSRF protection, XSS prevention, secure authentication
- **Performance**: Optimized database queries and static file handling
- **SEO Ready**: Search engine optimized with structured data
- **Social Ready**: Optimized for social media sharing

## 📝 License

This project is developed for educational and demonstration purposes.

---

**Note**: This is an active development project. Features are being added incrementally following professional development practices.