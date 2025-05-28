"""
Example configuration file for managing SOPs
This can be saved as config/sops_config.py
"""

# This is an example of how to externalize SOP configuration
# for easier management and scalability

SOPS_DATA = [
    {
        'id': 'data_processing',
        'title': 'Data Processing Script',
        'description': 'Learn how to process CSV files, clean data, and generate reports',
        'category': 'Data Processing',
        'difficulty': 'Beginner',
        'duration': '15 min',
        'link': 'https://example.com/sop/data-processing',
        'icon': '📊',
        'tags': ['CSV', 'Data', 'Reports'],
        'related_scripts': ['data_processor.py', 'csv_cleaner.py'],
        'sop_id': 'data_processing'  # Add this field
    },
    {
        'id': 'web_scraping',
        'title': 'Web Scraping Guide',
        'description': 'Step-by-step guide for setting up and running web scraping scripts',
        'category': 'Web Automation',
        'difficulty': 'Intermediate',
        'duration': '30 min',
        'link': 'https://example.com/sop/web-scraping',
        'icon': '🌐',
        'tags': ['Web', 'Scraping', 'Automation'],
        'related_scripts': ['web_scraper.py', 'selenium_bot.py']
    },
    {
        'id': 'image_processing',
        'title': 'Image Processing',
        'description': 'Batch process images with resizing, optimization, and format conversion',
        'category': 'Media Processing',
        'difficulty': 'Beginner',
        'duration': '10 min',
        'link': 'https://example.com/sop/image-processing',
        'icon': '🖼️',
        'tags': ['Images', 'Media', 'Batch']
    },
    {
        'id': 'api_integration',
        'title': 'API Integration Guide',
        'description': 'Connect to external APIs and process responses effectively',
        'category': 'Integration',
        'difficulty': 'Advanced',
        'duration': '45 min',
        'link': 'https://example.com/sop/api-integration',
        'icon': '🔌',
        'tags': ['API', 'Integration', 'REST']
    },

]

# Categories configuration
SOP_CATEGORIES = {
    'Data Processing': {
        'color': '#2196F3',
        'description': 'Scripts for processing and analyzing data'
    },
    'Web Automation': {
        'color': '#4CAF50',
        'description': 'Web scraping and browser automation'
    },
    'System Administration': {
        'color': '#FF9800',
        'description': 'System maintenance and administration tasks'
    },
    'Media Processing': {
        'color': '#9C27B0',
        'description': 'Image, video, and audio processing'
    },
    'Integration': {
        'color': '#F44336',
        'description': 'API and service integrations'
    },
    'Database': {
        'color': '#00BCD4',
        'description': 'Database operations and management'
    }
}

# Difficulty levels configuration
DIFFICULTY_LEVELS = {
    'Beginner': {
        'color': '#4CAF50',
        'estimated_time_multiplier': 1.0
    },
    'Intermediate': {
        'color': '#FF9800',
        'estimated_time_multiplier': 1.5
    },
    'Advanced': {
        'color': '#F44336',
        'estimated_time_multiplier': 2.0
    }
}

# To use this configuration in the SOPsPage:
# 1. Import at the top of sops_page.py:
#    from config.sops_config import SOPS_DATA, SOP_CATEGORIES, DIFFICULTY_LEVELS
#
# 2. In the __init__ method, replace self.sops_data with:
#    self.sops_data = SOPS_DATA
#
# This makes it easy to add new SOPs by just updating this configuration file!
