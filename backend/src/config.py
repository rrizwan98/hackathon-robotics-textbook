"""
Configuration for the backend application.
"""

import os

# Neon PostgreSQL Database URL
# The URL format: postgresql://user:password@host/database?sslmode=require
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_YnMftjp19BIH@ep-hidden-resonance-ahue1b4u-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

# Alternative direct connection string from user
NEON_DATABASE_URL = "postgresql://neondb_owner:npg_YnMftjp19BIH@ep-hidden-resonance-ahue1b4u-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Valid textbook sections for chat
VALID_TEXTBOOK_SECTIONS = [
    "Introduction to Physical AI & Humanoid Robotics",
    "Robot Operating System 2 (ROS2)"
]

