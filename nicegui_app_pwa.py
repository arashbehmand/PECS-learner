"""
PECS Learning System - NiceGUI PWA (Progressive Web App)
Docker-ready, mobile-optimized, installable web app

Run with Docker:
    docker-compose -f docker-compose.nicegui.yml up --build

Run locally:
    python nicegui_app_pwa.py

Access from anywhere:
    http://your-server-ip:8080
"""

import os
from pathlib import Path
from nicegui import ui, app
from utils.database import DatabaseRepository
from utils.models import Project
from datetime import datetime

# Initialize database
db = DatabaseRepository()

# PWA Configuration
PWA_MANIFEST = {
    "name": "P.E.C.S. Learning System",
    "short_name": "PECS Learn",
    "description": "Active learning system with AI-powered feedback and spaced repetition",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#3b82f6",
    "orientation": "portrait-primary",
    "icons": [
        {
            "src": "/static/icons/icon-72x72.png",
            "sizes": "72x72",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-96x96.png",
            "sizes": "96x96",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-128x128.png",
            "sizes": "128x128",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-144x144.png",
            "sizes": "144x144",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-152x152.png",
            "sizes": "152x152",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-192x192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any maskable"
        },
        {
            "src": "/static/icons/icon-384x384.png",
            "sizes": "384x384",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/icons/icon-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any maskable"
        }
    ],
    "categories": ["education", "productivity"],
    "screenshots": [
        {
            "src": "/static/screenshots/dashboard.png",
            "sizes": "1280x720",
            "type": "image/png"
        }
    ]
}

# Service Worker for offline support
SERVICE_WORKER_JS = """
const CACHE_NAME = 'pecs-learning-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => response || fetch(event.request))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
"""


def setup_pwa():
    """Setup PWA configuration and static files"""

    # Create static directories
    static_dir = Path('static')
    icons_dir = static_dir / 'icons'
    icons_dir.mkdir(parents=True, exist_ok=True)

    # Serve static files
    app.add_static_files('/static', str(static_dir))

    # Create manifest.json
    import json
    with open(static_dir / 'manifest.json', 'w') as f:
        json.dump(PWA_MANIFEST, f, indent=2)

    # Create service worker
    with open(static_dir / 'service-worker.js', 'w') as f:
        f.write(SERVICE_WORKER_JS)

    # Create a simple placeholder icon (you should replace with real icons)
    # For now, we'll just create a text file noting where icons should go
    with open(icons_dir / 'README.txt', 'w') as f:
        f.write("""
Place your app icons here:
- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

You can generate these from a single image using:
https://www.pwabuilder.com/imageGenerator
        """)

    # Add PWA meta tags and service worker registration to all pages
    ui.add_head_html('''
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="PECS Learn">
        <meta name="theme-color" content="#3b82f6">
        <link rel="manifest" href="/static/manifest.json">
        <link rel="apple-touch-icon" href="/static/icons/icon-192x192.png">
        <script>
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/service-worker.js')
                    .then(() => console.log('Service Worker registered'))
                    .catch((err) => console.error('Service Worker registration failed:', err));
            }
        </script>
    ''')


# Setup PWA
setup_pwa()


# ===== MOBILE-OPTIMIZED STYLES =====
def add_mobile_styles():
    """Add mobile-optimized CSS"""
    ui.add_head_html('''
        <style>
            /* Mobile-friendly responsive design */
            @media (max-width: 768px) {
                .desktop-only { display: none !important; }
                .q-page { padding: 0.5rem !important; }
                .text-3xl { font-size: 1.5rem !important; }
                .text-2xl { font-size: 1.25rem !important; }
                .gap-4 { gap: 0.5rem !important; }
            }

            /* Smooth transitions */
            * { transition: all 0.2s ease; }

            /* Touch-friendly buttons */
            button {
                min-height: 44px;
                min-width: 44px;
            }

            /* Better text readability */
            body {
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }

            /* Loading animation */
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .loading { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
        </style>
    ''')


add_mobile_styles()


# ===== RESPONSIVE LAYOUT HELPERS =====
def is_mobile():
    """Check if user is on mobile device (simplified)"""
    # In production, you'd use JavaScript to detect this properly
    return False  # Default to desktop layout


# ===== PAGE: Dashboard =====
@ui.page('/')
def dashboard():
    """Mobile-responsive dashboard"""

    # Add install prompt for PWA
    with ui.row().classes('w-full items-center justify-between p-4 bg-blue-50 rounded mb-4'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('install_mobile').classes('text-blue-600')
            ui.label('Install this app for offline access!').classes('text-sm')
        ui.button('Install', icon='download').props('flat dense').classes('text-blue-600')

    # Header (responsive)
    with ui.row().classes('w-full items-center justify-between mb-6 flex-wrap gap-4'):
        ui.label('📚 P.E.C.S. Learning').classes('text-2xl md:text-3xl font-bold')
        ui.button('➕ New', on_click=lambda: new_project_dialog.open()).classes('bg-blue-500')

    # Load projects
    projects = db.get_all_projects()

    if not projects:
        # Empty state (mobile-friendly)
        with ui.column().classes('items-center justify-center mt-12 px-4'):
            ui.icon('school').classes('text-6xl text-gray-400')
            ui.label('No projects yet').classes('text-xl text-gray-500 text-center')
            ui.label('Start learning by creating your first project').classes('text-gray-400 text-center')
            ui.button('Create Project', on_click=lambda: new_project_dialog.open()).classes('mt-4 bg-blue-500')
    else:
        # Responsive grid (1 col on mobile, 2 on tablet, 3 on desktop)
        with ui.grid(columns='repeat(auto-fill, minmax(280px, 1fr))').classes('w-full gap-4'):
            for project in projects:
                render_project_card(project)

    # New project dialog (mobile-optimized)
    with ui.dialog() as new_project_dialog, ui.card().classes('w-full max-w-md mx-4'):
        ui.label('Create New Project').classes('text-xl font-bold mb-4')

        project_name_input = ui.input(
            label='Project Name',
            placeholder='e.g., Learn Quantum Physics'
        ).classes('w-full').props('autofocus')

        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('Cancel', on_click=new_project_dialog.close).classes('bg-gray-300')
            ui.button(
                'Create',
                on_click=lambda: create_project(project_name_input.value, new_project_dialog)
            ).classes('bg-blue-500')


def render_project_card(project: Project):
    """Render a mobile-friendly project card"""

    stats = db.get_project_stats(project.id)

    with ui.card().classes('cursor-pointer hover:shadow-lg transition-shadow'):
        # Project header
        with ui.row().classes('w-full items-start justify-between mb-3'):
            ui.label(project.name).classes('text-lg font-bold flex-1')
            ui.icon('folder_open').classes('text-blue-500 text-xl')

        # Stats (mobile-optimized layout)
        with ui.row().classes('w-full gap-3 text-sm'):
            with ui.column().classes('items-center'):
                ui.label(str(stats['total_sections'])).classes('text-xl font-bold text-blue-600')
                ui.label('Sections').classes('text-xs text-gray-600')

            with ui.column().classes('items-center'):
                ui.label(str(stats['total_flashcards'])).classes('text-xl font-bold text-green-600')
                ui.label('Cards').classes('text-xs text-gray-600')

            with ui.column().classes('items-center'):
                ui.label(str(stats['completed_sections'])).classes('text-xl font-bold text-purple-600')
                ui.label('Done').classes('text-xs text-gray-600')

        # Progress
        if stats['total_sections'] > 0:
            progress = stats['completed_sections'] / stats['total_sections']
            ui.linear_progress(value=progress).classes('mt-3')
            ui.label(f"{int(progress * 100)}% Complete").classes('text-xs text-gray-500 mt-1')

        # Action buttons (touch-friendly)
        with ui.row().classes('w-full gap-2 mt-3'):
            ui.button(
                'Open',
                icon='arrow_forward',
                on_click=lambda p=project: open_project(p.id)
            ).classes('flex-1 bg-blue-500')

            ui.button(
                icon='delete',
                on_click=lambda p=project: delete_project_confirm(p)
            ).props('flat').classes('text-red-500')


def create_project(name: str, dialog):
    """Create a new project"""
    if not name or not name.strip():
        ui.notify('Please enter a project name', color='negative', position='top')
        return

    try:
        db.create_project(name.strip())
        ui.notify(f'Project "{name}" created!', color='positive', position='top')
        dialog.close()
        ui.navigate.reload()
    except Exception as e:
        ui.notify(f'Error: {str(e)}', color='negative', position='top')


def delete_project_confirm(project: Project):
    """Delete project with confirmation"""
    with ui.dialog() as confirm_dialog, ui.card().classes('max-w-sm mx-4'):
        ui.label(f'Delete "{project.name}"?').classes('text-lg font-bold')
        ui.label('This cannot be undone.').classes('text-gray-600 mt-2')

        with ui.row().classes('w-full gap-2 mt-4'):
            ui.button('Cancel', on_click=confirm_dialog.close).classes('flex-1 bg-gray-300')
            ui.button(
                'Delete',
                on_click=lambda: delete_project(project.id, confirm_dialog)
            ).classes('flex-1 bg-red-500')

    confirm_dialog.open()


def delete_project(project_id: int, dialog):
    """Delete a project"""
    try:
        db.delete_project(project_id)
        ui.notify('Project deleted', color='positive', position='top')
        dialog.close()
        ui.navigate.reload()
    except Exception as e:
        ui.notify(f'Error: {str(e)}', color='negative', position='top')


def open_project(project_id: int):
    """Navigate to project"""
    ui.navigate.to(f'/project/{project_id}')


# ===== PAGE: Project View =====
@ui.page('/project/{project_id}')
def project_view(project_id: int):
    """Mobile-optimized project view"""

    project = db.get_project(project_id)
    if not project:
        with ui.column().classes('items-center mt-12'):
            ui.label('Project not found').classes('text-xl text-red-500')
            ui.button('← Dashboard', on_click=lambda: ui.navigate.to('/')).classes('mt-4')
        return

    sections = db.get_sections_by_project(project_id)

    # Mobile-friendly header
    with ui.column().classes('w-full mb-6'):
        with ui.row().classes('w-full items-center gap-2 mb-3'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat')
            ui.label(project.name).classes('text-xl md:text-2xl font-bold flex-1')

        # Action buttons (stack on mobile)
        with ui.row().classes('w-full gap-2 flex-wrap'):
            ui.button('📚 Study', icon='school', on_click=lambda: ui.navigate.to(f'/study/{project_id}')).classes('bg-green-500 flex-1 min-w-32')
            ui.button('➕ Add Content', icon='add', on_click=lambda: ui.notify('Coming soon!', position='top')).classes('bg-blue-500 flex-1 min-w-32')

    if not sections:
        with ui.column().classes('items-center mt-12 px-4'):
            ui.icon('description').classes('text-6xl text-gray-400')
            ui.label('No content yet').classes('text-xl text-gray-500 text-center')
            ui.button('Upload Content', on_click=lambda: ui.notify('Coming soon!', position='top')).classes('mt-4')
    else:
        # Section list (mobile-optimized, no sidebar)
        ui.label('Sections').classes('text-lg font-bold mb-3')

        for idx, section in enumerate(sections):
            section_title = section.title or f"Section {idx + 1}"

            with ui.card().classes('w-full mb-3 cursor-pointer hover:shadow-md'):
                with ui.row().classes('w-full items-center gap-3'):
                    if section.is_completed:
                        ui.icon('check_circle').classes('text-green-500 text-xl')
                    else:
                        ui.icon('radio_button_unchecked').classes('text-gray-400 text-xl')

                    with ui.column().classes('flex-1'):
                        ui.label(section_title).classes('font-semibold')
                        if section.is_completed:
                            ui.label('Completed').classes('text-xs text-green-600')

                    ui.button(
                        icon='arrow_forward',
                        on_click=lambda s=section: ui.navigate.to(f'/learn/{project_id}/{s.id}')
                    ).props('flat dense').classes('text-blue-500')


# ===== PAGE: PECS Learning Interface (Mobile-Optimized) =====
@ui.page('/learn/{project_id}/{section_id}')
def pecs_learning(project_id: int, section_id: int):
    """Mobile-optimized PECS interface"""

    section = db.get_section(section_id)
    if not section:
        ui.label('Section not found').classes('text-xl text-red-500')
        return

    # Mobile-friendly header
    with ui.row().classes('w-full items-center gap-2 mb-4'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to(f'/project/{project_id}')).props('flat')
        ui.label(section.title or f"Section {section.order_index + 1}").classes('text-lg font-bold flex-1')

    # Vertical tabs on mobile, horizontal on desktop
    with ui.tabs().props('vertical' if is_mobile() else '').classes('w-full') as tabs:
        prime_tab = ui.tab('Prime', icon='visibility')
        engage_tab = ui.tab('Engage', icon='edit_note')
        challenge_tab = ui.tab('Challenge', icon='psychology')
        solidify_tab = ui.tab('Solidify', icon='workspace_premium')

    with ui.tab_panels(tabs, value=prime_tab).classes('w-full'):
        with ui.tab_panel(prime_tab):
            render_prime_phase_mobile(section)
        with ui.tab_panel(engage_tab):
            ui.label('Coming soon').classes('text-gray-500')
        with ui.tab_panel(challenge_tab):
            ui.label('Coming soon').classes('text-gray-500')
        with ui.tab_panel(solidify_tab):
            ui.label('Coming soon').classes('text-gray-500')


def render_prime_phase_mobile(section):
    """Mobile-optimized Prime phase"""

    pecs_data = section.pecs_data.get('prime_preview', {}) if section.pecs_data else {}

    with ui.column().classes('w-full space-y-4'):
        # Content (collapsible to save screen space)
        with ui.expansion('View Content', icon='book').classes('w-full bg-gray-50'):
            ui.markdown(section.content[:300] + '...' if len(section.content) > 300 else section.content)

        # Inputs (optimized for mobile typing)
        ui.label('What did you understand?').classes('font-semibold text-sm')
        understanding = ui.textarea(
            placeholder='Summarize...',
            value=pecs_data.get('initial_thoughts', '')
        ).classes('w-full').props('rows=4 autogrow')

        ui.label('Prior knowledge?').classes('font-semibold text-sm mt-4')
        prior = ui.textarea(
            placeholder='What you already know...',
            value=pecs_data.get('prior_knowledge', '')
        ).classes('w-full').props('rows=3 autogrow')

        ui.label('Questions?').classes('font-semibold text-sm mt-4')
        questions = ui.textarea(
            placeholder='What are you curious about?',
            value=pecs_data.get('questions', '')
        ).classes('w-full').props('rows=3 autogrow')

        # Touch-friendly action buttons
        with ui.row().classes('w-full gap-2 mt-4'):
            async def save():
                db.update_section_pecs_data(section.id, 'prime_preview', {
                    'initial_thoughts': understanding.value,
                    'prior_knowledge': prior.value,
                    'questions': questions.value
                })
                ui.notify('Saved!', color='positive', position='top')

            ui.button('Save', icon='save', on_click=save).classes('flex-1 bg-blue-500')
            ui.button('AI Feedback', icon='auto_awesome', on_click=lambda: ui.notify('Coming soon!', position='top')).classes('flex-1 bg-purple-500')


# ===== RUN APP =====
if __name__ in {"__main__", "__mp_main__"}:
    print("\n" + "="*70)
    print("🚀 PECS Learning System - PWA Edition")
    print("="*70)
    print("\n📱 Features:")
    print("   ✓ Mobile-optimized responsive design")
    print("   ✓ Progressive Web App (installable)")
    print("   ✓ Offline support with service worker")
    print("   ✓ Touch-friendly UI components")
    print("   ✓ Docker-ready for deployment")
    print("\n🌐 Access:")
    print("   • Local: http://localhost:8080")
    print("   • Network: http://<your-ip>:8080")
    print("\n📦 Deploy with Docker:")
    print("   docker-compose -f docker-compose.nicegui.yml up --build")
    print("\n" + "="*70 + "\n")

    ui.run(
        port=int(os.environ.get('PORT', 8080)),
        title='P.E.C.S. Learning System',
        favicon='📚',
        reload=True,
        show=False,
        # Enable for production deployment
        # host='0.0.0.0',
        # storage_secret='your-secret-key-here'  # Change in production!
    )
