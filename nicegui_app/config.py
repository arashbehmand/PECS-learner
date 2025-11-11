# -*- coding: utf-8 -*-
"""
Configuration for PECS Learning System - NiceGUI App
"""

import os
from pathlib import Path

# App metadata
APP_NAME = "P.E.C.S. Learning System"
APP_SHORT_NAME = "PECS Learn"
APP_VERSION = "2.0.0"  # NiceGUI version
APP_DESCRIPTION = (
    "Active learning system with AI-powered feedback and spaced repetition"
)

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = Path(__file__).parent / "static"

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
RELOAD = os.getenv("RELOAD", "false").lower() == "true"  # Enable for development

# Database
DATABASE_PATH = DATA_DIR / "pecs.db"

# Storage
NICEGUI_STORAGE_PATH = os.getenv(
    "NICEGUI_STORAGE_PATH", str(DATA_DIR / "nicegui_storage")
)

# Future: Multi-user support
ENABLE_AUTHENTICATION = os.getenv("ENABLE_AUTH", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")  # For sessions

# PWA Configuration
PWA_THEME_COLOR = "#3b82f6"  # Blue-500
PWA_BACKGROUND_COLOR = "#ffffff"

# UI Configuration
MOBILE_BREAKPOINT = 768  # px
SECTIONS_PER_PAGE = 20
CARDS_PER_STUDY_SESSION = 50

# AI Configuration (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_ENABLED = bool(OPENAI_API_KEY)

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)
