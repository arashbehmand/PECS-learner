# -*- coding: utf-8 -*-
"""
PECS Learning System - NiceGUI Main Application
Complete migration from Streamlit to NiceGUI with PWA support
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from utils/
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from nicegui import ui, app
from utils.database import DatabaseRepository
from nicegui_app import config

# Initialize database (singleton pattern)
_db_instance = None

def get_database() -> DatabaseRepository:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseRepository()
    return _db_instance


# ===== PWA SETUP =====
def setup_pwa():
    """Setup Progressive Web App configuration"""

    PWA_MANIFEST = {
        "name": config.APP_NAME,
        "short_name": config.APP_SHORT_NAME,
        "description": config.APP_DESCRIPTION,
        "start_url": "/",
        "display": "standalone",
        "background_color": config.PWA_BACKGROUND_COLOR,
        "theme_color": config.PWA_THEME_COLOR,
        "orientation": "portrait-primary",
        "icons": [
            {"src": "/static/icons/icon-192x192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icons/icon-512x512.png", "sizes": "512x512", "type": "image/png"}
        ],
        "categories": ["education", "productivity"]
    }

    SERVICE_WORKER_JS = """
    const CACHE_NAME = 'pecs-learning-v2';
    const urlsToCache = ['/', '/static/manifest.json'];

    self.addEventListener('install', (event) => {
      event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
      );
    });

    self.addEventListener('fetch', (event) => {
      event.respondWith(
        caches.match(event.request).then((response) => response || fetch(event.request))
      );
    });
    """

    # Create static files
    config.STATIC_DIR.mkdir(parents=True, exist_ok=True)
    icons_dir = config.STATIC_DIR / "icons"
    icons_dir.mkdir(exist_ok=True)

    # Write manifest
    with open(config.STATIC_DIR / "manifest.json", "w") as f:
        json.dump(PWA_MANIFEST, f, indent=2)

    # Write service worker
    with open(config.STATIC_DIR / "service-worker.js", "w") as f:
        f.write(SERVICE_WORKER_JS)

    # Serve static files
    app.add_static_files('/static', str(config.STATIC_DIR))

    # Add PWA meta tags
    ui.add_head_html(f'''
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="{config.APP_SHORT_NAME}">
        <meta name="theme-color" content="{config.PWA_THEME_COLOR}">
        <link rel="manifest" href="/static/manifest.json">
        <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
        <script>
            if ('serviceWorker' in navigator) {{
                navigator.serviceWorker.register('/static/service-worker.js')
                    .then(() => console.log('Service Worker registered'))
                    .catch((err) => console.error('SW registration failed:', err));
            }}
        </script>
    ''')

    # Mobile-optimized styles
    ui.add_head_html('''
        <style>
            /* Mobile-friendly responsive design */
            @media (max-width: 768px) {
                .desktop-only { display: none !important; }
                .q-page { padding: 0.5rem !important; }
                .text-3xl { font-size: 1.5rem !important; }
                .text-2xl { font-size: 1.25rem !important; }
            }

            /* Smooth transitions */
            * { transition: all 0.2s ease; }

            /* Touch-friendly buttons */
            button { min-height: 44px; min-width: 44px; }

            /* Better text readability */
            body {
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
        </style>
    ''')


# ===== ROUTING =====

@ui.page('/')
def dashboard_page():
    """Landing page - Project dashboard"""
    from nicegui_app.pages.dashboard import DashboardPage

    db = get_database()
    page = DashboardPage(db)
    page.render()


@ui.page('/project/{project_id}')
def project_view_page(project_id: int):
    """Project overview with sections"""
    from nicegui_app.pages.project_view import ProjectViewPage

    db = get_database()
    page = ProjectViewPage(db, project_id)
    page.render()


@ui.page('/project/{project_id}/upload')
def content_upload_page(project_id: int):
    """Upload content to project"""
    from nicegui_app.pages.content_upload import ContentUploadPage

    db = get_database()
    page = ContentUploadPage(db, project_id)
    page.render()


@ui.page('/project/{project_id}/study')
def study_mode_page(project_id: int):
    """Flashcard study mode"""
    from nicegui_app.pages.study_mode import StudyModePage

    db = get_database()
    page = StudyModePage(db, project_id)
    page.render()


@ui.page('/project/{project_id}/section/{section_id}')
def pecs_learning_page(project_id: int, section_id: int):
    """PECS 4-phase learning interface"""
    from nicegui_app.pages.pecs_learning import PECSLearningPage

    db = get_database()
    page = PECSLearningPage(db, project_id, section_id)
    page.render()


# ===== MAIN ENTRY POINT =====
if __name__ in {"__main__", "__mp_main__"}:
    print("\n" + "="*70)
    print(f"{config.APP_NAME} v{config.APP_VERSION}")
    print("="*70)
    print("\nFeatures:")
    print("   - Complete NiceGUI migration from Streamlit")
    print("   - Mobile-optimized responsive design")
    print("   - Progressive Web App (PWA) - installable")
    print("   - No page reloads - smooth UX")
    print("   - URL-based routing")
    print("   - Multi-user ready (auth scaffolding)")
    print("\nAccess:")
    print(f"   Local: http://localhost:{config.PORT}")
    print(f"   Network: http://<your-ip>:{config.PORT}")
    print("\nComponents:")
    print("   - Project Dashboard")
    print("   - Content Upload (EPUB, PDF, DOCX support)")
    print("   - PECS Learning (4-phase system)")
    print("   - Study Mode (spaced repetition)")
    print("   - Section Navigator")
    print("\n" + "="*70 + "\n")

    # Setup PWA on startup
    app.on_startup(setup_pwa)

    ui.run(
        port=config.PORT,
        host=config.HOST,
        title=config.APP_NAME,
        favicon='📚',
        reload=config.RELOAD,
        show=False,  # Don't auto-open browser
    )
