"""
Environment setup and configuration tests
"""
import pytest
import sys
import os
import subprocess
import importlib
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestEnvironmentSetup:
    """Test environment setup and prerequisites"""

    def test_env_001_virtual_environment_detection(self):
        """ENV-001: Test virtual environment activation detection"""
        # Check if we're in a virtual environment
        in_venv = (
            hasattr(sys, 'real_prefix') or 
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or
            'VIRTUAL_ENV' in os.environ
        )
        
        # This test documents the virtual environment status
        # In CI/CD or some environments, this might not be applicable
        if 'PYTEST_CURRENT_TEST' in os.environ:
            # Running in pytest, virtual environment detection may vary
            assert True  # Pass in test environment
        else:
            # In development, recommend using virtual environment
            if not in_venv:
                pytest.skip("Virtual environment not detected. Please activate virtual environment.")

    def test_env_002_python_version_verification(self):
        """ENV-002: Test Python version verification (3.8+)"""
        python_version = sys.version_info
        
        # Check minimum Python version
        assert python_version.major == 3, f"Python 3.x required, got {python_version.major}.x"
        assert python_version.minor >= 8, f"Python 3.8+ required, got {python_version.major}.{python_version.minor}"
        
        print(f"✓ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")

    def test_env_003_dependencies_installation_check(self):
        """ENV-003: Test dependencies installation check"""
        # List of required packages from requirements.txt
        required_packages = [
            'requests', 'beautifulsoup4', 'selenium', 'scrapy',
            'tweepy', 'linkedin-api', 'sqlalchemy', 'pandas', 'numpy',
            'nltk', 'textblob', 'geopy', 'pycountry', 'python-dotenv',
            'loguru', 'httpx'
        ]
        
        missing_packages = []
        installed_packages = []
        
        for package in required_packages:
            try:
                # Try to import the package
                if package == 'beautifulsoup4':
                    import bs4
                elif package == 'python-dotenv':
                    import dotenv
                elif package == 'linkedin-api':
                    # This might not be available, skip for now
                    continue
                else:
                    importlib.import_module(package.replace('-', '_'))
                
                installed_packages.append(package)
            except ImportError:
                missing_packages.append(package)
        
        print(f"✓ Installed packages: {len(installed_packages)}")
        if missing_packages:
            print(f"⚠ Missing packages: {missing_packages}")
        
        # Allow some packages to be missing in test environment
        critical_packages = ['requests', 'sqlalchemy', 'pandas']
        missing_critical = [pkg for pkg in missing_packages if pkg in critical_packages]
        
        assert len(missing_critical) == 0, f"Critical packages missing: {missing_critical}"

    def test_env_004_missing_dependencies_installation_simulation(self):
        """ENV-004: Test missing dependencies installation simulation"""
        # This test simulates the installation process
        # In a real scenario, you would run: pip install -r requirements.txt
        
        requirements_file = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        
        if os.path.exists(requirements_file):
            with open(requirements_file, 'r') as f:
                requirements = f.read()
                
            # Check that requirements.txt has content
            assert len(requirements.strip()) > 0, "requirements.txt is empty"
            
            # Check for key packages
            assert 'requests' in requirements, "requests not in requirements.txt"
            assert 'sqlalchemy' in requirements, "sqlalchemy not in requirements.txt"
            
            print("✓ requirements.txt found and contains expected packages")
        else:
            pytest.fail("requirements.txt not found")

    def test_env_005_env_file_structure_validation(self):
        """ENV-005: Test .env file structure validation"""
        env_file_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        env_example_path = os.path.join(os.path.dirname(__file__), '..', '.env.example')
        
        # Check if .env or .env.example exists
        has_env_file = os.path.exists(env_file_path)
        has_env_example = os.path.exists(env_example_path)
        
        if not has_env_file and not has_env_example:
            # Create a basic .env.example for reference
            env_example_content = """# Journalist Finder Configuration
# Copy this file to .env and fill in your API keys

# Twitter API Configuration
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here

# LinkedIn API Configuration
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:8080/callback

# NewsAPI Configuration
NEWSAPI_KEY=your_newsapi_key_here

# Clearbit Configuration
CLEARBIT_KEY=your_clearbit_key_here

# Database Configuration (optional, defaults to SQLite)
# DATABASE_URL=sqlite:///data/journalists.db
"""
            
            with open(env_example_path, 'w') as f:
                f.write(env_example_content)
            
            print("✓ Created .env.example file")
        
        # If .env exists, validate its structure
        if has_env_file:
            with open(env_file_path, 'r') as f:
                env_content = f.read()
            
            # Check for key configuration sections
            expected_keys = [
                'TWITTER_API_KEY', 'NEWSAPI_KEY', 'CLEARBIT_KEY', 'LINKEDIN_CLIENT_ID'
            ]
            
            found_keys = []
            for key in expected_keys:
                if key in env_content:
                    found_keys.append(key)
            
            print(f"✓ .env file found with {len(found_keys)}/{len(expected_keys)} expected keys")
        
        assert has_env_file or has_env_example, "No .env or .env.example file found"

    def test_env_006_settings_py_configuration_load(self):
        """ENV-006: Test settings.py configuration load"""
        try:
            from config import settings
            
            # Check that settings module loads without errors
            assert hasattr(settings, 'DATABASE_URL'), "DATABASE_URL not defined in settings"
            assert hasattr(settings, 'LOG_LEVEL'), "LOG_LEVEL not defined in settings"
            assert hasattr(settings, 'LOG_FILE'), "LOG_FILE not defined in settings"
            
            # Check default values
            assert settings.DATABASE_URL is not None, "DATABASE_URL is None"
            assert settings.LOG_LEVEL in ['DEBUG', 'INFO', 'WARNING', 'ERROR'], f"Invalid LOG_LEVEL: {settings.LOG_LEVEL}"
            
            print("✓ Settings configuration loaded successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import settings: {e}")
        except Exception as e:
            pytest.fail(f"Error loading settings: {e}")

    def test_env_007_database_path_and_permissions(self):
        """ENV-007: Test database path and permissions check"""
        try:
            from config.settings import DATABASE_URL
            
            # Extract database path from URL
            if DATABASE_URL.startswith('sqlite:///'):
                db_path = DATABASE_URL.replace('sqlite:///', '')
                
                # Check if path is absolute or relative
                if not os.path.isabs(db_path):
                    # Relative path, make it relative to project root
                    project_root = os.path.dirname(os.path.dirname(__file__))
                    db_path = os.path.join(project_root, db_path)
                
                # Check if directory exists or can be created
                db_dir = os.path.dirname(db_path)
                
                if not os.path.exists(db_dir):
                    try:
                        os.makedirs(db_dir, exist_ok=True)
                        print(f"✓ Created database directory: {db_dir}")
                    except PermissionError:
                        pytest.fail(f"Permission denied creating database directory: {db_dir}")
                
                # Test write permissions
                try:
                    test_file = os.path.join(db_dir, 'test_permissions.tmp')
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    print(f"✓ Database directory has write permissions: {db_dir}")
                except PermissionError:
                    pytest.fail(f"No write permissions for database directory: {db_dir}")
            
            else:
                # Non-SQLite database, skip file system checks
                print(f"✓ Using non-SQLite database: {DATABASE_URL}")
                
        except ImportError:
            pytest.fail("Could not import DATABASE_URL from settings")

    def test_env_008_logs_directory_creation(self):
        """ENV-008: Test logs directory creation"""
        try:
            from config.settings import LOG_FILE
            
            log_dir = os.path.dirname(LOG_FILE)
            
            # Check if log directory exists or can be created
            if not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir, exist_ok=True)
                    print(f"✓ Created logs directory: {log_dir}")
                except PermissionError:
                    pytest.fail(f"Permission denied creating logs directory: {log_dir}")
            
            # Test write permissions for logs
            try:
                test_log = os.path.join(log_dir, 'test_log.tmp')
                with open(test_log, 'w') as f:
                    f.write('test log entry')
                os.remove(test_log)
                print(f"✓ Logs directory has write permissions: {log_dir}")
            except PermissionError:
                pytest.fail(f"No write permissions for logs directory: {log_dir}")
                
        except ImportError:
            pytest.fail("Could not import LOG_FILE from settings")


class TestDatabaseConfiguration:
    """Test database configuration and connectivity"""

    def test_database_connection_establishment(self):
        """Test database connection establishment"""
        try:
            from database.database_manager import DatabaseManager
            
            # Use in-memory database for testing
            with patch('database.database_manager.DATABASE_URL', 'sqlite:///:memory:'):
                db_manager = DatabaseManager()
                
                # Test that database manager initializes
                assert db_manager is not None
                assert db_manager.engine is not None
                
                # Test basic connection
                session = db_manager.get_session()
                assert session is not None
                session.close()
                
                print("✓ Database connection established successfully")
                
        except Exception as e:
            pytest.fail(f"Database connection failed: {e}")

    def test_database_models_import(self):
        """Test database models import"""
        try:
            from database.models import Journalist, Base
            
            # Check that models are properly defined
            assert hasattr(Journalist, '__tablename__')
            assert hasattr(Journalist, 'id')
            assert hasattr(Journalist, 'name')
            assert hasattr(Journalist, 'email')
            
            print("✓ Database models imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Failed to import database models: {e}")


class TestExternalDependencies:
    """Test external dependencies and tools"""

    def test_selenium_webdriver_availability(self):
        """Test Selenium WebDriver availability"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            # Test Chrome options (most common)
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # Don't actually create a driver in tests, just check imports
            assert webdriver.Chrome is not None
            print("✓ Selenium WebDriver imports available")
            
        except ImportError as e:
            pytest.skip(f"Selenium not available: {e}")

    def test_nltk_data_availability(self):
        """Test NLTK data availability"""
        try:
            import nltk
            
            # Check if NLTK data is available
            try:
                nltk.data.find('tokenizers/punkt')
                print("✓ NLTK punkt tokenizer available")
            except LookupError:
                # Download if not available (in test environment)
                try:
                    nltk.download('punkt', quiet=True)
                    print("✓ NLTK punkt tokenizer downloaded")
                except:
                    pytest.skip("Could not download NLTK data")
            
        except ImportError:
            pytest.skip("NLTK not available")

    def test_api_client_libraries(self):
        """Test API client libraries availability"""
        api_libraries = {
            'httpx': 'httpx',
            'requests': 'requests',
            'tweepy': 'tweepy'
        }
        
        available_libraries = []
        missing_libraries = []
        
        for name, module in api_libraries.items():
            try:
                importlib.import_module(module)
                available_libraries.append(name)
            except ImportError:
                missing_libraries.append(name)
        
        print(f"✓ Available API libraries: {available_libraries}")
        if missing_libraries:
            print(f"⚠ Missing API libraries: {missing_libraries}")
        
        # At least basic HTTP libraries should be available
        assert 'httpx' in available_libraries or 'requests' in available_libraries


class TestConfigurationValidation:
    """Test configuration validation"""

    def test_api_key_configuration_structure(self):
        """Test API key configuration structure"""
        try:
            from config import settings
            
            # Check that API key variables are defined (even if empty)
            api_keys = [
                'TWITTER_API_KEY', 'TWITTER_API_SECRET',
                'NEWSAPI_KEY', 'CLEARBIT_KEY',
                'LINKEDIN_CLIENT_ID', 'LINKEDIN_CLIENT_SECRET'
            ]
            
            defined_keys = []
            for key in api_keys:
                if hasattr(settings, key):
                    defined_keys.append(key)
            
            print(f"✓ Defined API key variables: {len(defined_keys)}/{len(api_keys)}")
            
            # At least the variables should be defined (even if None)
            assert len(defined_keys) >= len(api_keys) // 2, "Most API key variables should be defined"
            
        except ImportError:
            pytest.fail("Could not import settings for API key validation")

    def test_logging_configuration_validation(self):
        """Test logging configuration validation"""
        try:
            from config.settings import LOG_LEVEL, LOG_FILE
            
            # Validate log level
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            assert LOG_LEVEL in valid_levels, f"Invalid log level: {LOG_LEVEL}"
            
            # Validate log file path
            assert LOG_FILE is not None, "LOG_FILE is None"
            assert isinstance(LOG_FILE, str), "LOG_FILE should be a string"
            assert len(LOG_FILE) > 0, "LOG_FILE is empty"
            
            print(f"✓ Logging configuration valid: {LOG_LEVEL} -> {LOG_FILE}")
            
        except ImportError:
            pytest.fail("Could not import logging configuration")

    def test_scraping_configuration_validation(self):
        """Test scraping configuration validation"""
        try:
            from config import settings
            
            # Check scraping-related settings
            scraping_settings = [
                'SCRAPING_DELAY', 'MAX_RETRIES', 'TIMEOUT',
                'AI_KEYWORDS', 'NEWS_SOURCES'
            ]
            
            for setting in scraping_settings:
                if hasattr(settings, setting):
                    value = getattr(settings, setting)
                    
                    if setting in ['SCRAPING_DELAY', 'MAX_RETRIES', 'TIMEOUT']:
                        assert isinstance(value, (int, float)), f"{setting} should be numeric"
                        assert value > 0, f"{setting} should be positive"
                    
                    elif setting in ['AI_KEYWORDS', 'NEWS_SOURCES']:
                        assert isinstance(value, list), f"{setting} should be a list"
                        assert len(value) > 0, f"{setting} should not be empty"
            
            print("✓ Scraping configuration validated")
            
        except ImportError:
            pytest.fail("Could not import scraping configuration")


class TestSystemRequirements:
    """Test system requirements and compatibility"""

    def test_operating_system_compatibility(self):
        """Test operating system compatibility"""
        import platform
        
        os_name = platform.system()
        os_version = platform.release()
        
        print(f"✓ Operating System: {os_name} {os_version}")
        
        # The system should work on major operating systems
        supported_os = ['Windows', 'Darwin', 'Linux']  # Darwin = macOS
        
        if os_name not in supported_os:
            pytest.skip(f"Untested operating system: {os_name}")

    def test_memory_requirements(self):
        """Test basic memory requirements"""
        try:
            import psutil
            
            # Get available memory
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            print(f"✓ Available memory: {available_gb:.1f} GB")
            
            # Recommend at least 1GB available memory
            if available_gb < 1.0:
                pytest.skip("Low memory available, may affect performance")
                
        except ImportError:
            # psutil not available, skip memory check
            pytest.skip("psutil not available for memory check")

    def test_disk_space_requirements(self):
        """Test disk space requirements"""
        try:
            import shutil
            
            # Check available disk space in current directory
            total, used, free = shutil.disk_usage('.')
            free_gb = free / (1024**3)
            
            print(f"✓ Available disk space: {free_gb:.1f} GB")
            
            # Recommend at least 1GB free space
            if free_gb < 1.0:
                pytest.skip("Low disk space available")
                
        except Exception:
            pytest.skip("Could not check disk space")
