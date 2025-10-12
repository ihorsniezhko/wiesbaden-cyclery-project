# SEO Implementation

## Overview

Strategic SEO implementation maximizes search visibility for valuable content while excluding utility pages.

## Page Indexing Strategy

### NOINDEX Pages (9 pages)
Excluded from search results with `<meta name="robots" content="noindex, follow">`:
- Shopping Cart, Checkout, Order Confirmation, Order Tracking
- Login, Signup, Password Reset (3 pages)

### INDEX Pages (~57 pages)
Included in search results:
- Home page, 50 Product pages, 6 Category pages, Legal pages

## Configuration

### Robots.txt
**Location:** `templates/robots.txt`

**Blocked:** `/admin/`, `/accounts/`, `/cart/`, `/orders/`, `/profile/`  
**Allowed:** `/products/`, `/static/`, `/media/`  
**Sitemap:** `/sitemap.xml`

### Sitemap
**Location:** `wiesbaden_cyclery/sitemaps.py`

| Type | Pages | Priority | Frequency |
|------|-------|----------|-----------|
| Static | Home, Legal | 0.5 | Monthly |
| Products | ~50 in-stock | 0.8 | Weekly |
| Categories | 6 categories | 0.6 | Monthly |

## Testing

**Local:**
- Robots: `http://localhost:8000/robots.txt`
- Sitemap: `http://localhost:8000/sitemap.xml`

**Production:**
- Robots: `https://wiesbaden-cyclery-project-818faeff3e83.herokuapp.com/robots.txt`
- Sitemap: `https://wiesbaden-cyclery-project-818faeff3e83.herokuapp.com/sitemap.xml`

## Post-Deployment

**Immediate:**
- Submit sitemap to Google Search Console and Bing Webmaster Tools
- Verify robots.txt and sitemap.xml load correctly

**Week 1:**
- Verify NOINDEX pages excluded
- Request indexing for key product pages

**Month 1:**
- Confirm ~60 pages indexed, 0 utility pages indexed

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Utility pages in search | Verify NOINDEX tag, request removal in Search Console |
| Products not indexed | Check robots.txt, verify sitemap, request indexing |
| Sitemap errors | Verify sitemap.xml loads, check all URLs valid |
| Crawl errors | Review Search Console, fix broken links |
