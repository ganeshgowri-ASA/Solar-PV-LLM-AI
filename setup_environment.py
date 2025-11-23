#!/usr/bin/env python3
"""
Solar PV LLM AI - Environment Setup Script

This script helps set up the environment configuration for the Solar PV LLM AI project.
It provides an interactive setup wizard and validates the configuration.

Usage:
    python setup_environment.py              # Interactive setup
    python setup_environment.py --check      # Check existing configuration
    python setup_environment.py --copy       # Just copy .env.example to .env
"""

import os
import sys
import argparse
import secrets
from pathlib import Path
from typing import Dict, Optional, Tuple
import shutil


# Project root directory
PROJECT_ROOT = Path(__file__).parent.resolve()
ENV_EXAMPLE_PATH = PROJECT_ROOT / ".env.example"
ENV_PATH = PROJECT_ROOT / ".env"


def print_header() -> None:
    """Print script header."""
    print("\n" + "=" * 60)
    print("  Solar PV LLM AI - Environment Setup")
    print("=" * 60 + "\n")


def print_success(message: str) -> None:
    """Print success message."""
    print(f"[OK] {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    print(f"[!] {message}")


def print_error(message: str) -> None:
    """Print error message."""
    print(f"[ERROR] {message}")


def print_info(message: str) -> None:
    """Print info message."""
    print(f"[INFO] {message}")


def check_env_example_exists() -> bool:
    """Check if .env.example file exists."""
    if not ENV_EXAMPLE_PATH.exists():
        print_error(f".env.example not found at {ENV_EXAMPLE_PATH}")
        return False
    return True


def copy_env_example() -> bool:
    """Copy .env.example to .env if .env doesn't exist."""
    if ENV_PATH.exists():
        response = input("\n.env already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print_info("Keeping existing .env file.")
            return True

    try:
        shutil.copy(ENV_EXAMPLE_PATH, ENV_PATH)
        print_success(f"Created {ENV_PATH}")
        return True
    except Exception as e:
        print_error(f"Failed to copy .env.example: {e}")
        return False


def read_env_file() -> Dict[str, str]:
    """Read current .env file and return as dictionary."""
    env_vars = {}
    if not ENV_PATH.exists():
        return env_vars

    with open(ENV_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                env_vars[key.strip()] = value.strip()

    return env_vars


def write_env_file(env_vars: Dict[str, str]) -> bool:
    """Write environment variables to .env file, preserving comments."""
    try:
        # Read original .env.example to preserve structure and comments
        with open(ENV_EXAMPLE_PATH, 'r') as f:
            lines = f.readlines()

        # Update values while preserving structure
        updated_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and '=' in stripped:
                key, _, _ = stripped.partition('=')
                key = key.strip()
                if key in env_vars and env_vars[key]:
                    updated_lines.append(f"{key}={env_vars[key]}\n")
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        with open(ENV_PATH, 'w') as f:
            f.writelines(updated_lines)

        print_success(f"Updated {ENV_PATH}")
        return True
    except Exception as e:
        print_error(f"Failed to write .env file: {e}")
        return False


def prompt_for_value(key: str, description: str, current_value: str = "", secret: bool = False) -> str:
    """Prompt user for a configuration value."""
    if current_value and not secret:
        prompt = f"{description}\n  [{key}] (current: {current_value[:20]}...): "
    elif current_value and secret:
        prompt = f"{description}\n  [{key}] (currently set, press Enter to keep): "
    else:
        prompt = f"{description}\n  [{key}]: "

    value = input(prompt).strip()

    if not value and current_value:
        return current_value
    return value


def generate_secret_key() -> str:
    """Generate a secure secret key."""
    return secrets.token_hex(32)


def interactive_setup() -> None:
    """Run interactive setup wizard."""
    print_header()
    print("This wizard will help you configure the Solar PV LLM AI project.\n")
    print("Press Enter to skip optional fields or keep existing values.\n")

    if not check_env_example_exists():
        sys.exit(1)

    if not copy_env_example():
        sys.exit(1)

    env_vars = read_env_file()

    # LLM API Keys
    print("\n" + "-" * 40)
    print("LLM API Configuration")
    print("-" * 40)
    print("At least one LLM API key is required.\n")

    env_vars['OPENAI_API_KEY'] = prompt_for_value(
        'OPENAI_API_KEY',
        "OpenAI API Key (https://platform.openai.com/api-keys):",
        env_vars.get('OPENAI_API_KEY', ''),
        secret=True
    )

    env_vars['ANTHROPIC_API_KEY'] = prompt_for_value(
        'ANTHROPIC_API_KEY',
        "Anthropic API Key (https://console.anthropic.com/):",
        env_vars.get('ANTHROPIC_API_KEY', ''),
        secret=True
    )

    env_vars['GOOGLE_API_KEY'] = prompt_for_value(
        'GOOGLE_API_KEY',
        "Google API Key (https://makersuite.google.com/app/apikey):",
        env_vars.get('GOOGLE_API_KEY', ''),
        secret=True
    )

    env_vars['COHERE_API_KEY'] = prompt_for_value(
        'COHERE_API_KEY',
        "Cohere API Key for embeddings (https://dashboard.cohere.com/api-keys):",
        env_vars.get('COHERE_API_KEY', ''),
        secret=True
    )

    # Pinecone Configuration
    print("\n" + "-" * 40)
    print("Pinecone Vector Database Configuration")
    print("-" * 40)

    env_vars['PINECONE_API_KEY'] = prompt_for_value(
        'PINECONE_API_KEY',
        "Pinecone API Key (https://app.pinecone.io/):",
        env_vars.get('PINECONE_API_KEY', ''),
        secret=True
    )

    env_vars['PINECONE_ENVIRONMENT'] = prompt_for_value(
        'PINECONE_ENVIRONMENT',
        "Pinecone Environment (e.g., us-west-2):",
        env_vars.get('PINECONE_ENVIRONMENT', 'us-west-2')
    )

    env_vars['PINECONE_INDEX_NAME'] = prompt_for_value(
        'PINECONE_INDEX_NAME',
        "Pinecone Index Name:",
        env_vars.get('PINECONE_INDEX_NAME', 'pv-expert-knowledge')
    )

    # NREL API Key
    print("\n" + "-" * 40)
    print("External API Configuration")
    print("-" * 40)

    env_vars['NREL_API_KEY'] = prompt_for_value(
        'NREL_API_KEY',
        "NREL API Key (https://developer.nrel.gov/signup/):",
        env_vars.get('NREL_API_KEY', ''),
        secret=True
    )

    # Database Configuration
    print("\n" + "-" * 40)
    print("Database Configuration")
    print("-" * 40)

    env_vars['DATABASE_URL'] = prompt_for_value(
        'DATABASE_URL',
        "PostgreSQL Database URL:",
        env_vars.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/solar_pv_ai')
    )

    env_vars['REDIS_URL'] = prompt_for_value(
        'REDIS_URL',
        "Redis URL:",
        env_vars.get('REDIS_URL', 'redis://localhost:6379/0')
    )

    # Application Settings
    print("\n" + "-" * 40)
    print("Application Settings")
    print("-" * 40)

    env_vars['ENVIRONMENT'] = prompt_for_value(
        'ENVIRONMENT',
        "Environment (development/staging/production):",
        env_vars.get('ENVIRONMENT', 'development')
    )

    env_vars['DEBUG'] = prompt_for_value(
        'DEBUG',
        "Debug Mode (True/False):",
        env_vars.get('DEBUG', 'False')
    )

    env_vars['LOG_LEVEL'] = prompt_for_value(
        'LOG_LEVEL',
        "Log Level (DEBUG/INFO/WARNING/ERROR):",
        env_vars.get('LOG_LEVEL', 'INFO')
    )

    # Generate secret key if not set
    if not env_vars.get('SECRET_KEY'):
        print("\nNo SECRET_KEY found. Generating a secure key...")
        env_vars['SECRET_KEY'] = generate_secret_key()
        print_success("Generated new SECRET_KEY")

    # Write the configuration
    print("\n" + "-" * 40)
    print("Saving Configuration")
    print("-" * 40)

    if write_env_file(env_vars):
        print_success("Configuration saved successfully!")
    else:
        print_error("Failed to save configuration")
        sys.exit(1)

    # Offer to validate
    print("\n" + "-" * 40)
    validate = input("Would you like to validate the configuration? (Y/n): ").strip().lower()
    if validate != 'n':
        check_configuration()


def check_configuration() -> bool:
    """Check and validate current configuration."""
    print("\n" + "-" * 40)
    print("Configuration Validation")
    print("-" * 40 + "\n")

    if not ENV_PATH.exists():
        print_error(".env file not found. Run setup first.")
        return False

    env_vars = read_env_file()
    has_errors = False
    has_warnings = False

    # Check LLM API Keys
    llm_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY']
    configured_llms = [k for k in llm_keys if env_vars.get(k)]

    if not configured_llms:
        print_error("No LLM API keys configured. At least one is required.")
        has_errors = True
    else:
        for key in configured_llms:
            print_success(f"{key} is configured")

    # Check Pinecone
    if env_vars.get('PINECONE_API_KEY'):
        print_success("PINECONE_API_KEY is configured")
        print_info(f"  Environment: {env_vars.get('PINECONE_ENVIRONMENT', 'not set')}")
        print_info(f"  Index: {env_vars.get('PINECONE_INDEX_NAME', 'not set')}")
    else:
        print_warning("PINECONE_API_KEY not configured (vector search unavailable)")
        has_warnings = True

    # Check NREL
    if env_vars.get('NREL_API_KEY'):
        print_success("NREL_API_KEY is configured")
    else:
        print_warning("NREL_API_KEY not configured (solar data features unavailable)")
        has_warnings = True

    # Check Cohere
    if env_vars.get('COHERE_API_KEY'):
        print_success("COHERE_API_KEY is configured")
    else:
        print_info("COHERE_API_KEY not configured (optional)")

    # Check Database
    if env_vars.get('DATABASE_URL'):
        print_success(f"DATABASE_URL is configured")
    else:
        print_warning("DATABASE_URL not configured")
        has_warnings = True

    # Check Redis
    if env_vars.get('REDIS_URL'):
        print_success(f"REDIS_URL is configured")
    else:
        print_warning("REDIS_URL not configured")
        has_warnings = True

    # Check Secret Key
    if env_vars.get('SECRET_KEY'):
        print_success("SECRET_KEY is configured")
    else:
        print_warning("SECRET_KEY not configured (will be required in production)")
        has_warnings = True

    # Check Environment
    environment = env_vars.get('ENVIRONMENT', 'development')
    debug = env_vars.get('DEBUG', 'False').lower() == 'true'

    if environment == 'production' and debug:
        print_error("DEBUG should be False in production!")
        has_errors = True

    if environment == 'production' and not env_vars.get('SECRET_KEY'):
        print_error("SECRET_KEY is required in production!")
        has_errors = True

    # Summary
    print("\n" + "-" * 40)
    if has_errors:
        print_error("Configuration has errors that must be fixed.")
        return False
    elif has_warnings:
        print_warning("Configuration has warnings. Some features may be unavailable.")
        return True
    else:
        print_success("Configuration looks good!")
        return True


def test_connections() -> None:
    """Test API connections (optional)."""
    print("\n" + "-" * 40)
    print("Testing API Connections")
    print("-" * 40 + "\n")

    env_vars = read_env_file()

    # Test OpenAI
    if env_vars.get('OPENAI_API_KEY'):
        try:
            import openai
            client = openai.OpenAI(api_key=env_vars['OPENAI_API_KEY'])
            client.models.list()
            print_success("OpenAI API connection successful")
        except ImportError:
            print_info("OpenAI package not installed. Skipping test.")
        except Exception as e:
            print_error(f"OpenAI API connection failed: {e}")

    # Test Anthropic
    if env_vars.get('ANTHROPIC_API_KEY'):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=env_vars['ANTHROPIC_API_KEY'])
            # Just verify the client initializes
            print_success("Anthropic API key format valid")
        except ImportError:
            print_info("Anthropic package not installed. Skipping test.")
        except Exception as e:
            print_error(f"Anthropic API validation failed: {e}")

    # Test Pinecone
    if env_vars.get('PINECONE_API_KEY'):
        try:
            from pinecone import Pinecone
            pc = Pinecone(api_key=env_vars['PINECONE_API_KEY'])
            pc.list_indexes()
            print_success("Pinecone API connection successful")
        except ImportError:
            print_info("Pinecone package not installed. Skipping test.")
        except Exception as e:
            print_error(f"Pinecone API connection failed: {e}")

    print("\n" + "-" * 40)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Solar PV LLM AI - Environment Setup Script"
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check and validate existing configuration'
    )
    parser.add_argument(
        '--copy',
        action='store_true',
        help='Just copy .env.example to .env'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test API connections'
    )
    parser.add_argument(
        '--generate-key',
        action='store_true',
        help='Generate a new SECRET_KEY'
    )

    args = parser.parse_args()

    if args.generate_key:
        print(f"Generated SECRET_KEY: {generate_secret_key()}")
        return

    if args.copy:
        print_header()
        if check_env_example_exists():
            copy_env_example()
        return

    if args.check:
        print_header()
        check_configuration()
        return

    if args.test:
        print_header()
        if check_configuration():
            test_connections()
        return

    # Default: interactive setup
    interactive_setup()


if __name__ == "__main__":
    main()
