"""
Webhook monitoring and analytics utilities
"""
import logging
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

# Cache keys for webhook monitoring
WEBHOOK_STATS_PREFIX = 'webhook_stats_'
WEBHOOK_ERRORS_PREFIX = 'webhook_errors_'
WEBHOOK_RATE_PREFIX = 'webhook_rate_'

def record_webhook_event(event_type, success=True, processing_time=None, error=None):
    """
    Record webhook event for monitoring and analytics
    """
    now = timezone.now()
    date_key = now.strftime('%Y-%m-%d')
    hour_key = now.strftime('%Y-%m-%d-%H')
    
    # Record daily stats
    daily_stats_key = f"{WEBHOOK_STATS_PREFIX}daily_{date_key}"
    daily_stats = cache.get(daily_stats_key, defaultdict(lambda: {'count': 0, 'success': 0, 'errors': 0}))
    
    daily_stats[event_type]['count'] += 1
    if success:
        daily_stats[event_type]['success'] += 1
    else:
        daily_stats[event_type]['errors'] += 1
    
    cache.set(daily_stats_key, daily_stats, 86400 * 7)  # Keep for 7 days
    
    # Record hourly stats for rate monitoring
    hourly_rate_key = f"{WEBHOOK_RATE_PREFIX}{hour_key}"
    hourly_count = cache.get(hourly_rate_key, 0)
    cache.set(hourly_rate_key, hourly_count + 1, 3600)  # Keep for 1 hour
    
    # Record processing time if provided
    if processing_time:
        perf_key = f"{WEBHOOK_STATS_PREFIX}perf_{date_key}"
        perf_stats = cache.get(perf_key, {'total_time': 0, 'count': 0, 'max_time': 0})
        perf_stats['total_time'] += processing_time
        perf_stats['count'] += 1
        perf_stats['max_time'] = max(perf_stats['max_time'], processing_time)
        cache.set(perf_key, perf_stats, 86400 * 7)
    
    # Record errors for debugging
    if error:
        error_key = f"{WEBHOOK_ERRORS_PREFIX}{date_key}"
        errors = cache.get(error_key, [])
        errors.append({
            'timestamp': now.isoformat(),
            'event_type': event_type,
            'error': str(error)[:500],  # Limit error message length
        })
        # Keep only last 100 errors
        if len(errors) > 100:
            errors = errors[-100:]
        cache.set(error_key, errors, 86400 * 7)

def get_webhook_stats(days=7):
    """
    Get webhook statistics for the specified number of days
    """
    stats = {}
    now = timezone.now()
    
    for i in range(days):
        date = now - timedelta(days=i)
        date_key = date.strftime('%Y-%m-%d')
        daily_stats_key = f"{WEBHOOK_STATS_PREFIX}daily_{date_key}"
        
        daily_data = cache.get(daily_stats_key, {})
        if daily_data:
            stats[date_key] = daily_data
    
    return stats

def get_webhook_performance(days=7):
    """
    Get webhook performance statistics
    """
    performance = {}
    now = timezone.now()
    
    for i in range(days):
        date = now - timedelta(days=i)
        date_key = date.strftime('%Y-%m-%d')
        perf_key = f"{WEBHOOK_STATS_PREFIX}perf_{date_key}"
        
        perf_data = cache.get(perf_key, {})
        if perf_data and perf_data['count'] > 0:
            performance[date_key] = {
                'avg_time': perf_data['total_time'] / perf_data['count'],
                'max_time': perf_data['max_time'],
                'total_events': perf_data['count']
            }
    
    return performance

def get_webhook_errors(days=7):
    """
    Get recent webhook errors
    """
    all_errors = []
    now = timezone.now()
    
    for i in range(days):
        date = now - timedelta(days=i)
        date_key = date.strftime('%Y-%m-%d')
        error_key = f"{WEBHOOK_ERRORS_PREFIX}{date_key}"
        
        errors = cache.get(error_key, [])
        all_errors.extend(errors)
    
    # Sort by timestamp (newest first)
    all_errors.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return all_errors

def check_webhook_health():
    """
    Check webhook system health and return status
    """
    now = timezone.now()
    current_hour = now.strftime('%Y-%m-%d-%H')
    previous_hour = (now - timedelta(hours=1)).strftime('%Y-%m-%d-%H')
    
    # Check current hour activity
    current_rate = cache.get(f"{WEBHOOK_RATE_PREFIX}{current_hour}", 0)
    previous_rate = cache.get(f"{WEBHOOK_RATE_PREFIX}{previous_hour}", 0)
    
    # Get recent errors
    recent_errors = get_webhook_errors(days=1)
    error_count = len(recent_errors)
    
    # Get performance data
    performance = get_webhook_performance(days=1)
    avg_performance = 0
    if performance:
        avg_performance = sum(p['avg_time'] for p in performance.values()) / len(performance)
    
    # Determine health status
    health_status = 'healthy'
    issues = []
    
    if error_count > 10:  # More than 10 errors in last 24 hours
        health_status = 'warning'
        issues.append(f'High error rate: {error_count} errors in last 24 hours')
    
    if avg_performance > 5.0:  # Average processing time > 5 seconds
        health_status = 'warning'
        issues.append(f'Slow processing: {avg_performance:.2f}s average')
    
    if current_rate == 0 and previous_rate == 0:
        # No webhook activity might indicate a problem
        health_status = 'info'
        issues.append('No recent webhook activity')
    
    return {
        'status': health_status,
        'current_hour_events': current_rate,
        'previous_hour_events': previous_rate,
        'recent_errors': error_count,
        'avg_processing_time': avg_performance,
        'issues': issues,
        'last_checked': now.isoformat()
    }

def generate_webhook_report():
    """
    Generate a comprehensive webhook report
    """
    stats = get_webhook_stats(days=7)
    performance = get_webhook_performance(days=7)
    errors = get_webhook_errors(days=7)
    health = check_webhook_health()
    
    # Calculate totals
    total_events = 0
    total_success = 0
    total_errors = 0
    
    for date_stats in stats.values():
        for event_stats in date_stats.values():
            total_events += event_stats['count']
            total_success += event_stats['success']
            total_errors += event_stats['errors']
    
    success_rate = (total_success / total_events * 100) if total_events > 0 else 0
    
    return {
        'summary': {
            'total_events': total_events,
            'success_rate': success_rate,
            'total_errors': total_errors,
            'health_status': health['status']
        },
        'daily_stats': stats,
        'performance': performance,
        'recent_errors': errors[:10],  # Last 10 errors
        'health_check': health
    }