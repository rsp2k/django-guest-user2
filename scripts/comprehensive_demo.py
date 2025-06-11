#!/usr/bin/env python3
import os
import sys
import logging
import time
import shutil
from datetime import datetime
from playwright.sync_api import sync_playwright

# Set up logging for the demo script
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('demo_process.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('guest_user_demo')

# Define the base URL for your running Django project
BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:8000')

# Comprehensive URL test cases based on the django-guest-user2 URL structure
URLS_TO_TEST = [
    {
        'path': '/',
        'name': 'homepage',
        'title': 'Django Guest User Demo Homepage',
        'description': 'Main homepage demonstrating django-guest-user2 functionality with navigation',
        'user_type': 'anonymous',
        'category': 'Navigation'
    },
    {
        'path': '/',
        'name': 'homepage_guest',
        'title': 'Homepage (Guest User)',
        'description': 'Homepage accessed by a guest user showing dynamic user status',
        'user_type': 'guest',
        'category': 'Navigation'
    },
    {
        'path': '/',
        'name': 'homepage_admin',
        'title': 'Homepage (Admin User)',
        'description': 'Homepage accessed by an admin user showing different user status',
        'user_type': 'admin',
        'category': 'Navigation'
    },
    {
        'path': '/admin/',
        'name': 'admin_login',
        'title': 'Django Admin Login',
        'description': 'Django admin login page - Anonymous user should see login form',
        'user_type': 'anonymous',
        'category': 'Admin Interface'
    },
    {
        'path': '/admin/',
        'name': 'admin_dashboard',
        'title': 'Django Admin Dashboard',
        'description': 'Django admin dashboard - Logged-in admin should see admin interface',
        'user_type': 'admin',
        'requires_login': True,
        'category': 'Admin Interface'
    },
    {
        'path': '/allow_guest_user/',
        'name': 'allow_guest_user_anonymous',
        'title': 'Allow Guest User (Anonymous)',
        'description': 'Allow guest user view - Anonymous user gets auto-created guest session',
        'user_type': 'anonymous',
        'category': 'Decorator Views'
    },
    {
        'path': '/allow_guest_user/',
        'name': 'allow_guest_user_guest',
        'title': 'Allow Guest User (Guest)',
        'description': 'Allow guest user view - Guest user accesses normally',
        'user_type': 'guest',
        'category': 'Decorator Views'
    },
    {
        'path': '/allow_guest_user/',
        'name': 'allow_guest_user_regular',
        'title': 'Allow Guest User (Regular)',
        'description': 'Allow guest user view - Regular user accesses normally',
        'user_type': 'admin',
        'category': 'Decorator Views'
    },
    {
        'path': '/guest_user_required/',
        'name': 'guest_user_required_anonymous',
        'title': 'Guest User Required (Anonymous)',
        'description': 'Guest user required view - Anonymous user gets converted to guest automatically',
        'user_type': 'anonymous',
        'category': 'Decorator Views'
    },
    {
        'path': '/guest_user_required/',
        'name': 'guest_user_required_guest',
        'title': 'Guest User Required (Guest)',
        'description': 'Guest user required view - Guest user accesses normally',
        'user_type': 'guest',
        'category': 'Decorator Views'
    },
    {
        'path': '/regular_user_required/',
        'name': 'regular_user_required_anonymous',
        'title': 'Regular User Required (Anonymous)',
        'description': 'Regular user required view - Anonymous user should be redirected to login',
        'user_type': 'anonymous',
        'category': 'Decorator Views'
    },
    {
        'path': '/regular_user_required/',
        'name': 'regular_user_required_admin',
        'title': 'Regular User Required (Admin)',
        'description': 'Regular user required view - Admin user accesses normally',
        'user_type': 'admin',
        'category': 'Decorator Views'
    },
    {
        'path': '/mixin/allow_guest_user/',
        'name': 'mixin_allow_guest_user',
        'title': 'Allow Guest User Mixin',
        'description': 'Mixin-based allow guest user view - Class-based view equivalent',
        'user_type': 'guest',
        'category': 'Mixin Views'
    },
    {
        'path': '/mixin/guest_user_required/',
        'name': 'mixin_guest_user_required',
        'title': 'Guest User Required Mixin',
        'description': 'Mixin-based guest user required view - Class-based view equivalent',
        'user_type': 'guest',
        'category': 'Mixin Views'
    },
    {
        'path': '/mixin/regular_user_required/',
        'name': 'mixin_regular_user_required',
        'title': 'Regular User Required Mixin',
        'description': 'Mixin-based regular user required view - Class-based view equivalent',
        'user_type': 'admin',
        'category': 'Mixin Views'
    },
    {
        'path': '/convert/',
        'name': 'convert_form_anonymous',
        'title': 'Convert Form (Anonymous)',
        'description': 'Guest conversion form - Anonymous user should be redirected to login first',
        'user_type': 'anonymous',
        'category': 'Conversion Workflow'
    },
    {
        'path': '/convert/',
        'name': 'convert_form_guest',
        'title': 'Convert Form (Guest User)',
        'description': 'Guest conversion form - Guest user sees conversion form to become regular user',
        'user_type': 'guest',
        'interactive': True,
        'category': 'Conversion Workflow'
    },
    {
        'path': '/convert/success/',
        'name': 'convert_success',
        'title': 'Conversion Success Page',
        'description': 'Guest conversion success page - Shows after successful conversion',
        'user_type': 'guest',
        'category': 'Conversion Workflow'
    }
]

OUTPUT_DIR = 'screenshots'
VIDEO_DIR = 'videos'
WEB_DIR = 'web_demo'

def setup_output_directories():
    """Create output directories for screenshots, videos, and web demo."""
    for directory in [OUTPUT_DIR, VIDEO_DIR, WEB_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

def create_guest_user_session(context):
    """Create a browser context with a guest user session."""
    page = context.new_page()
    
    # Visit a guest-user-required page to trigger guest user creation
    logger.info("Creating guest user session...")
    page.goto(f"{BASE_URL}/guest_user_required/")
    page.wait_for_timeout(2000)
    
    logger.info("Guest user session established")
    return page

def login_admin_user(context, username, password):
    """Log in as admin user."""
    page = context.new_page()
    
    logger.info("Logging in as admin user...")
    page.goto(f"{BASE_URL}/admin/login/")
    page.wait_for_selector('input[name="username"]', timeout=10000)
    
    page.fill('input[name="username"]', username)
    page.wait_for_timeout(500)
    page.fill('input[name="password"]', password)
    page.wait_for_timeout(500)
    
    page.click('input[type="submit"]')
    
    try:
        page.wait_for_selector('h1:has-text("Django administration")', timeout=10000)
        logger.info("Admin login successful!")
        return page
    except:
        logger.error("Admin login failed")
        return None

def capture_url_with_user_type(context, url_info, admin_credentials=None):
    """
    Capture URL with specific user type and create meaningful video filename.
    """
    url_path = url_info['path']
    name = url_info['name']
    title = url_info['title']
    description = url_info['description']
    user_type = url_info['user_type']
    interactive = url_info.get('interactive', False)
    category = url_info['category']
    
    full_url = f"{BASE_URL}{url_path}"
    
    # Create meaningful video filename
    safe_title = title.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')
    video_filename = f"{name}_{safe_title}.webm"
    
    try:
        logger.info(f"Testing {name}: {title} [User: {user_type}]")
        
        # Create a dedicated page for this capture with video recording
        page = context.new_page()
        
        # Set up the appropriate user session on this page
        if user_type == 'guest':
            # First visit guest_user_required to establish guest session
            page.goto(f"{BASE_URL}/guest_user_required/")
            page.wait_for_timeout(1000)
        elif user_type == 'admin' and admin_credentials:
            # Login as admin on this page
            page.goto(f"{BASE_URL}/admin/login/")
            page.wait_for_selector('input[name="username"]', timeout=10000)
            page.fill('input[name="username"]', admin_credentials[0])
            page.wait_for_timeout(300)
            page.fill('input[name="password"]', admin_credentials[1])
            page.wait_for_timeout(300)
            page.click('input[type="submit"]')
            page.wait_for_timeout(2000)
        
        # Navigate to the target URL
        logger.info(f"Navigating to {full_url}")
        page.goto(full_url, wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(3000)
        
        # Handle interactive pages
        if interactive and url_path == '/convert/':
            demonstrate_conversion_form(page)
        
        # Take screenshot
        screenshot_path = os.path.join(OUTPUT_DIR, f"{name}.png")
        page.screenshot(path=screenshot_path, full_page=True)
        logger.info(f"Screenshot saved: {screenshot_path}")
        
        # Additional wait for video content
        page.wait_for_timeout(2000)
        
        # Log current page state
        current_url = page.url
        if current_url != full_url:
            logger.info(f"Redirected from {full_url} to {current_url}")
        
        try:
            page_title = page.title()
            logger.info(f"Page title: {page_title}")
        except:
            page_title = "Unknown"
        
        # Close the page to finalize video
        page.close()
        
        # Try to find and rename the video file with meaningful name
        video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.webm')]
        if video_files:
            # Get the most recently created video file
            latest_video = max([os.path.join(VIDEO_DIR, f) for f in video_files], key=os.path.getctime)
            new_video_path = os.path.join(VIDEO_DIR, video_filename)
            
            # Rename to meaningful name if it's not already named correctly
            if latest_video != new_video_path and os.path.exists(latest_video):
                try:
                    shutil.move(latest_video, new_video_path)
                    logger.info(f"Video saved as: {video_filename}")
                except:
                    logger.info(f"Video saved as: {os.path.basename(latest_video)}")
                    video_filename = os.path.basename(latest_video)
        
        return {
            'success': True,
            'screenshot': f"{name}.png",
            'video': video_filename,
            'current_url': current_url,
            'page_title': page_title
        }
        
    except Exception as e:
        logger.error(f"Failed to capture {name}: {e}")
        return {
            'success': False,
            'screenshot': None,
            'video': None,
            'current_url': None,
            'page_title': None
        }

def demonstrate_conversion_form(page):
    """
    Demonstrate the guest user to regular user conversion form.
    """
    try:
        logger.info("Demonstrating guest user conversion form...")
        page.wait_for_timeout(2000)
        
        # Look for form fields
        username_field = page.query_selector('input[name="username"]')
        password1_field = page.query_selector('input[name="password1"]')
        password2_field = page.query_selector('input[name="password2"]')
        
        if username_field and password1_field and password2_field:
            logger.info("Filling out conversion form...")
            
            username_field.fill("demo_converted_user")
            page.wait_for_timeout(800)
            
            password1_field.fill("demo_password_123")
            page.wait_for_timeout(800)
            
            password2_field.fill("demo_password_123")
            page.wait_for_timeout(800)
            
            logger.info("Form filled (not submitted for demo purposes)")
        else:
            logger.info("Conversion form fields not found as expected")
            
    except Exception as e:
        logger.warning(f"Error demonstrating conversion form: {e}")

def create_html_index(capture_results):
    """
    Create an HTML index page showcasing all screenshots and videos.
    """
    logger.info("Creating HTML index page...")
    
    # Group results by category
    categories = {}
    for result in capture_results:
        category = result['url_info']['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(result)
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Django Guest User Comprehensive Demo</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
        }}
        .stats {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .category {{
            margin-bottom: 40px;
        }}
        .category h2 {{
            color: #3498db;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .demo-item {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            margin-bottom: 25px;
            overflow: hidden;
        }}
        .demo-header {{
            background: #e9ecef;
            padding: 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        .demo-title {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            margin: 0;
        }}
        .demo-description {{
            color: #6c757d;
            margin: 5px 0 0 0;
            font-size: 0.9em;
        }}
        .demo-content {{
            padding: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        .screenshot-section, .video-section {{
            text-align: center;
        }}
        .screenshot-section h4, .video-section h4 {{
            color: #495057;
            margin-bottom: 15px;
        }}
        .screenshot {{
            max-width: 100%;
            height: auto;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        video {{
            width: 100%;
            max-width: 500px;
            height: auto;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .user-type {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .user-type.anonymous {{
            background: #ffeaa7;
            color: #e17055;
        }}
        .user-type.guest {{
            background: #81ecec;
            color: #00b894;
        }}
        .user-type.admin {{
            background: #a29bfe;
            color: #6c5ce7;
        }}
        .status {{
            float: right;
        }}
        .status.success {{
            color: #00b894;
        }}
        .status.failed {{
            color: #e17055;
        }}
        .meta-info {{
            font-size: 0.8em;
            color: #6c757d;
            margin-top: 10px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
        }}
        @media (max-width: 768px) {{
            .demo-content {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎭 Django Guest User Comprehensive Demo</h1>
        <p class="subtitle">Complete visual demonstration of django-guest-user2 functionality</p>
        
        <div class="stats">
            <h3>📊 Demo Statistics</h3>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
            <p><strong>Total Tests:</strong> {len(capture_results)} URL/user combinations</p>
            <p><strong>Successful:</strong> {len([r for r in capture_results if r['result']['success']])} captures</p>
            <p><strong>Categories:</strong> {len(categories)} functional areas</p>
        </div>
'''

    # Add categories
    for category_name, items in categories.items():
        html_content += f'''
        <div class="category">
            <h2>🔧 {category_name}</h2>
'''
        
        for item in items:
            url_info = item['url_info']
            result = item['result']
            
            status_class = 'success' if result['success'] else 'failed'
            status_text = '✅ Success' if result['success'] else '❌ Failed'
            
            html_content += f'''
            <div class="demo-item">
                <div class="demo-header">
                    <div class="demo-title">
                        {url_info['title']}
                        <span class="user-type {url_info['user_type']}">{url_info['user_type']}</span>
                        <span class="status {status_class}">{status_text}</span>
                    </div>
                    <div class="demo-description">{url_info['description']}</div>
                    <div class="meta-info">
                        <strong>URL:</strong> {url_info['path']} |
                        <strong>User Type:</strong> {url_info['user_type'].title()}
'''

            if result['current_url'] and result['current_url'] != f"{BASE_URL}{url_info['path']}":
                html_content += f''' | <strong>Redirected to:</strong> {result['current_url']}'''
            
            html_content += '''
                    </div>
                </div>
'''
            
            if result['success']:
                html_content += '''
                <div class="demo-content">
                    <div class="screenshot-section">
                        <h4>📸 Screenshot</h4>
'''
                if result['screenshot']:
                    html_content += f'''
                        <img src="../{OUTPUT_DIR}/{result['screenshot']}" alt="{url_info['title']} Screenshot" class="screenshot">
'''
                else:
                    html_content += '''
                        <p>Screenshot not available</p>
'''
                
                html_content += '''
                    </div>
                    <div class="video-section">
                        <h4>🎥 Video Demonstration</h4>
'''
                if result['video']:
                    html_content += f'''
                        <video controls preload="metadata">
                            <source src="../{VIDEO_DIR}/{result['video']}" type="video/webm">
                            Your browser does not support the video tag.
                        </video>
'''
                else:
                    html_content += '''
                        <p>Video not available</p>
'''
                
                html_content += '''
                    </div>
                </div>
'''
            else:
                html_content += '''
                <div class="demo-content">
                    <p style="text-align: center; color: #e17055; padding: 20px;">
                        ⚠️ This demonstration failed to capture. Check the logs for more details.
                    </p>
                </div>
'''
            
            html_content += '''
            </div>
'''
        
        html_content += '''
        </div>
'''

    html_content += f'''
        <div class="footer">
            <p>Generated by django-guest-user2 automated testing workflow</p>
            <p>🔗 <a href="https://github.com/rsp2k/django-guest-user2">django-guest-user2 on GitHub</a></p>
        </div>
    </div>
</body>
</html>'''
    
    # Write HTML file
    html_path = os.path.join(WEB_DIR, 'index.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"HTML index created: {html_path}")
    return html_path

def main():
    setup_output_directories()

    # Get admin credentials from environment variables
    admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    admin_credentials = (admin_username, admin_password) if admin_username and admin_password else None

    logger.info(f"Starting comprehensive guest user demo at {datetime.now()}")
    logger.info(f"Base URL: {BASE_URL}")
    logger.info(f"Output directories: {OUTPUT_DIR}, {VIDEO_DIR}, {WEB_DIR}")
    logger.info(f"Testing {len(URLS_TO_TEST)} different URL/user combinations")

    with sync_playwright() as p:
        # Launch browser with video recording enabled
        browser = p.chromium.launch(
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        # Create browser context with video recording
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            record_video_dir=VIDEO_DIR,
            record_video_size={'width': 1920, 'height': 1080}
        )
        
        capture_results = []
        
        # Test each URL with its specified user type
        for url_info in URLS_TO_TEST:
            result = capture_url_with_user_type(context, url_info, admin_credentials)
            capture_results.append({
                'url_info': url_info,
                'result': result
            })

        # Close browser context and browser
        context.close()
        browser.close()
        
        # Create HTML index page
        html_path = create_html_index(capture_results)
        
        # Print comprehensive summary
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE GUEST USER DEMO SUMMARY")
        logger.info("="*80)
        successful = sum(1 for item in capture_results if item['result']['success'])
        total = len(capture_results)
        logger.info(f"Successfully captured: {successful}/{total} URL/user combinations")
        
        logger.info("\nResults by user type:")
        for user_type in ['anonymous', 'guest', 'admin']:
            user_results = [item for item in capture_results if item['url_info']['user_type'] == user_type]
            user_successful = sum(1 for item in user_results if item['result']['success'])
            logger.info(f"  {user_type.title()} user: {user_successful}/{len(user_results)} successful")
        
        logger.info("\nResults by category:")
        categories = {}
        for item in capture_results:
            category = item['url_info']['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        for category, items in categories.items():
            cat_successful = sum(1 for item in items if item['result']['success'])
            logger.info(f"  {category}: {cat_successful}/{len(items)} successful")
        
        # List generated files
        logger.info("\n" + "="*80)
        logger.info("GENERATED FILES")
        logger.info("="*80)
        
        screenshot_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.png')] if os.path.exists(OUTPUT_DIR) else []
        video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.webm')] if os.path.exists(VIDEO_DIR) else []
        
        logger.info(f"📄 HTML Index: {html_path}")
        logger.info(f"📸 Screenshots ({len(screenshot_files)}):")
        for f in sorted(screenshot_files):
            logger.info(f"    {f}")
        
        logger.info(f"🎥 Videos ({len(video_files)}):")
        for f in sorted(video_files):
            logger.info(f"    {f}")
        
        if successful == 0:
            logger.error("\n⚠️  WARNING: No URLs were captured successfully!")
            sys.exit(1)
        elif successful < total:
            logger.warning(f"\n⚠️  WARNING: {total - successful} URLs failed to capture")
        else:
            logger.info(f"\n🎉 All URLs captured successfully!")
            
        logger.info(f"\n🔖 View the complete demo at: {html_path}")
        logger.info(f"Demo completed at {datetime.now()}")

if __name__ == '__main__':
    main()
