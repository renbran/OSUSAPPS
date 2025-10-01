"""
Odoo 17 MCP Server - Enhanced Configuration System

This module provides comprehensive configuration management with:
- Environment variable loading from .env files
- Cross-platform compatibility (Windows/Linux/macOS)
- Secure credential management
- Configuration validation
- Default values with overrides
"""

import os
import sys
import platform
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import logging

# Try to import python-dotenv, fallback gracefully
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv not available. Install with: pip install python-dotenv")


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 5432
    user: str = "odoo"
    password: str = "odoo"
    default_database: str = "odoo"
    connection_timeout: int = 30
    max_connections: int = 10

    def get_connection_params(self) -> Dict[str, Any]:
        """Get connection parameters for psycopg2."""
        return {
            'host': self.host,
            'port': self.port,
            'user': self.user,
            'password': self.password,
            'connect_timeout': self.connection_timeout
        }

    def get_connection_string(self, database: Optional[str] = None) -> str:
        """Get PostgreSQL connection string."""
        db = database or self.default_database
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{db}"


@dataclass
class DockerConfig:
    """Docker and Docker Compose configuration."""
    compose_file: str = "docker-compose.yml"
    odoo_service: str = "odoo"
    db_service: str = "db"
    use_docker_compose_v2: bool = True  # Use 'docker compose' instead of 'docker-compose'
    compose_timeout: int = 300

    def get_compose_command(self) -> List[str]:
        """Get the appropriate docker compose command for the platform."""
        if self.use_docker_compose_v2:
            return ['docker', 'compose']
        else:
            return ['docker-compose']

    def get_compose_file_arg(self) -> List[str]:
        """Get compose file argument if needed."""
        if self.compose_file and self.compose_file != "docker-compose.yml":
            return ['-f', self.compose_file]
        return []


@dataclass
class PathConfig:
    """Path configuration with cross-platform support."""
    odoo_addons_path: str = "/mnt/extra-addons"
    log_path: str = "/var/log/odoo"
    backup_path: str = "./backups"
    temp_path: str = None  # Will use system temp by default

    def __post_init__(self):
        """Set platform-specific defaults."""
        if self.temp_path is None:
            import tempfile
            self.temp_path = tempfile.gettempdir()

        # Convert to Path objects for easier handling
        self.backup_path = str(Path(self.backup_path).resolve())

    def get_odoo_log_path(self, is_docker: bool = True) -> str:
        """Get the appropriate Odoo log path."""
        if is_docker:
            return self.log_path
        elif platform.system() == "Windows":
            return str(Path(os.getenv('APPDATA', '.')) / 'Odoo' / 'logs')
        else:
            return self.log_path

    def ensure_backup_dir(self) -> Path:
        """Ensure backup directory exists and return Path object."""
        backup_dir = Path(self.backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir


@dataclass
class OdooConfig:
    """Odoo-specific configuration."""
    version: str = "17.0"
    admin_password: str = "admin"
    default_language: str = "en_US"
    default_timezone: str = "UTC"
    http_port: int = 8069
    longpolling_port: int = 8072
    workers: int = 4
    max_cron_threads: int = 2

    def get_odoo_url(self, host: str = "localhost") -> str:
        """Get the Odoo instance URL."""
        return f"http://{host}:{self.http_port}"


@dataclass
class CodeQualityConfig:
    """Code quality tools configuration."""
    flake8_max_line_length: int = 88
    flake8_ignore: List[str] = field(default_factory=lambda: ['E203', 'W503', 'E501'])
    pylint_disable: List[str] = field(default_factory=lambda: ['C0114', 'C0115', 'C0116'])
    black_line_length: int = 88
    enable_auto_fix: bool = False
    enable_pre_commit: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    def get_log_level(self) -> int:
        """Get logging level as integer."""
        return getattr(logging, self.level.upper(), logging.INFO)


@dataclass
class SecurityConfig:
    """Security configuration."""
    enable_input_validation: bool = True
    max_query_length: int = 10000
    allowed_query_keywords: List[str] = field(default_factory=lambda: ['SELECT'])
    blocked_query_keywords: List[str] = field(default_factory=lambda: [
        'DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE'
    ])
    max_subprocess_timeout: int = 300
    enable_command_whitelist: bool = True
    allowed_shell_commands: List[str] = field(default_factory=lambda: [
        'docker', 'docker-compose', 'git', 'pip', 'python', 'pytest', 'flake8', 'pylint', 'black'
    ])


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    enable_caching: bool = True
    cache_ttl: int = 300  # 5 minutes
    max_cache_size: int = 1000
    enable_connection_pooling: bool = True
    subprocess_use_async: bool = True
    max_concurrent_operations: int = 5


class Config:
    """Main configuration class that aggregates all settings."""

    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration from environment and .env file."""
        self.platform = platform.system()
        self.is_windows = self.platform == "Windows"
        self.is_linux = self.platform == "Linux"
        self.is_macos = self.platform == "Darwin"

        # Load environment variables from .env file
        if env_file is None:
            # Look for .env in the mcp_server directory
            env_file = Path(__file__).parent / ".env"

        if DOTENV_AVAILABLE and Path(env_file).exists():
            load_dotenv(env_file)
            self.env_file_loaded = True
        else:
            self.env_file_loaded = False

        # Initialize all configuration sections
        self.database = self._load_database_config()
        self.docker = self._load_docker_config()
        self.paths = self._load_path_config()
        self.odoo = self._load_odoo_config()
        self.code_quality = self._load_code_quality_config()
        self.logging = self._load_logging_config()
        self.security = self._load_security_config()
        self.performance = self._load_performance_config()

        # Validate configuration
        self.validate()

    def _get_env(self, key: str, default: Any = None, cast_type: type = str) -> Any:
        """Get environment variable with type casting."""
        value = os.getenv(key, default)
        if value is None:
            return default

        if cast_type == bool:
            return str(value).lower() in ('true', '1', 'yes', 'on')
        elif cast_type == int:
            try:
                return int(value)
            except (ValueError, TypeError):
                return default
        elif cast_type == list:
            return [item.strip() for item in str(value).split(',') if item.strip()]
        else:
            return cast_type(value)

    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration from environment."""
        return DatabaseConfig(
            host=self._get_env('DB_HOST', 'localhost'),
            port=self._get_env('DB_PORT', 5432, int),
            user=self._get_env('DB_USER', 'odoo'),
            password=self._get_env('DB_PASSWORD', 'odoo'),
            default_database=self._get_env('DB_NAME', 'odoo'),
            connection_timeout=self._get_env('DB_TIMEOUT', 30, int),
            max_connections=self._get_env('DB_MAX_CONNECTIONS', 10, int)
        )

    def _load_docker_config(self) -> DockerConfig:
        """Load Docker configuration from environment."""
        return DockerConfig(
            compose_file=self._get_env('COMPOSE_FILE', 'docker-compose.yml'),
            odoo_service=self._get_env('ODOO_SERVICE', 'odoo'),
            db_service=self._get_env('DB_SERVICE', 'db'),
            use_docker_compose_v2=self._get_env('USE_DOCKER_COMPOSE_V2', True, bool),
            compose_timeout=self._get_env('COMPOSE_TIMEOUT', 300, int)
        )

    def _load_path_config(self) -> PathConfig:
        """Load path configuration from environment."""
        return PathConfig(
            odoo_addons_path=self._get_env('ODOO_ADDONS_PATH', '/mnt/extra-addons'),
            log_path=self._get_env('LOG_PATH', '/var/log/odoo'),
            backup_path=self._get_env('BACKUP_PATH', './backups'),
            temp_path=self._get_env('TEMP_PATH', None)
        )

    def _load_odoo_config(self) -> OdooConfig:
        """Load Odoo configuration from environment."""
        return OdooConfig(
            version=self._get_env('ODOO_VERSION', '17.0'),
            admin_password=self._get_env('ODOO_ADMIN_PASSWORD', 'admin'),
            default_language=self._get_env('ODOO_LANG', 'en_US'),
            default_timezone=self._get_env('ODOO_TIMEZONE', 'UTC'),
            http_port=self._get_env('ODOO_HTTP_PORT', 8069, int),
            longpolling_port=self._get_env('ODOO_LONGPOLLING_PORT', 8072, int),
            workers=self._get_env('ODOO_WORKERS', 4, int),
            max_cron_threads=self._get_env('ODOO_MAX_CRON_THREADS', 2, int)
        )

    def _load_code_quality_config(self) -> CodeQualityConfig:
        """Load code quality configuration from environment."""
        return CodeQualityConfig(
            flake8_max_line_length=self._get_env('FLAKE8_MAX_LINE_LENGTH', 88, int),
            flake8_ignore=self._get_env('FLAKE8_IGNORE', ['E203', 'W503', 'E501'], list),
            pylint_disable=self._get_env('PYLINT_DISABLE', ['C0114', 'C0115', 'C0116'], list),
            black_line_length=self._get_env('BLACK_LINE_LENGTH', 88, int),
            enable_auto_fix=self._get_env('ENABLE_AUTO_FIX', False, bool),
            enable_pre_commit=self._get_env('ENABLE_PRE_COMMIT', True, bool)
        )

    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration from environment."""
        return LoggingConfig(
            level=self._get_env('LOG_LEVEL', 'INFO'),
            format=self._get_env('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file=self._get_env('LOG_FILE', None),
            max_bytes=self._get_env('LOG_MAX_BYTES', 10 * 1024 * 1024, int),
            backup_count=self._get_env('LOG_BACKUP_COUNT', 5, int)
        )

    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration from environment."""
        return SecurityConfig(
            enable_input_validation=self._get_env('SECURITY_INPUT_VALIDATION', True, bool),
            max_query_length=self._get_env('SECURITY_MAX_QUERY_LENGTH', 10000, int),
            max_subprocess_timeout=self._get_env('SECURITY_MAX_TIMEOUT', 300, int),
            enable_command_whitelist=self._get_env('SECURITY_COMMAND_WHITELIST', True, bool)
        )

    def _load_performance_config(self) -> PerformanceConfig:
        """Load performance configuration from environment."""
        return PerformanceConfig(
            enable_caching=self._get_env('PERF_ENABLE_CACHING', True, bool),
            cache_ttl=self._get_env('PERF_CACHE_TTL', 300, int),
            max_cache_size=self._get_env('PERF_MAX_CACHE_SIZE', 1000, int),
            enable_connection_pooling=self._get_env('PERF_CONNECTION_POOLING', True, bool),
            subprocess_use_async=self._get_env('PERF_ASYNC_SUBPROCESS', True, bool),
            max_concurrent_operations=self._get_env('PERF_MAX_CONCURRENT', 5, int)
        )

    def validate(self) -> None:
        """Validate configuration settings."""
        errors = []

        # Validate database port
        if not (1 <= self.database.port <= 65535):
            errors.append(f"Invalid database port: {self.database.port}")

        # Validate Odoo ports
        if not (1 <= self.odoo.http_port <= 65535):
            errors.append(f"Invalid Odoo HTTP port: {self.odoo.http_port}")

        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level.upper() not in valid_levels:
            errors.append(f"Invalid log level: {self.logging.level}. Must be one of {valid_levels}")

        # Validate paths exist or can be created
        try:
            self.paths.ensure_backup_dir()
        except Exception as e:
            errors.append(f"Cannot create backup directory: {e}")

        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (for debugging)."""
        return {
            'platform': self.platform,
            'env_file_loaded': self.env_file_loaded,
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'user': self.database.user,
                'password': '***HIDDEN***',
                'default_database': self.database.default_database
            },
            'docker': {
                'compose_file': self.docker.compose_file,
                'odoo_service': self.docker.odoo_service,
                'use_docker_compose_v2': self.docker.use_docker_compose_v2
            },
            'odoo': {
                'version': self.odoo.version,
                'http_port': self.odoo.http_port,
                'workers': self.odoo.workers
            },
            'performance': {
                'enable_caching': self.performance.enable_caching,
                'cache_ttl': self.performance.cache_ttl,
                'subprocess_use_async': self.performance.subprocess_use_async
            }
        }

    def print_summary(self) -> str:
        """Get a summary of the current configuration."""
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║         Odoo 17 MCP Server Configuration Summary            ║
╚══════════════════════════════════════════════════════════════╝

🖥️  Platform: {self.platform}
📄 .env file: {'Loaded ✅' if self.env_file_loaded else 'Not found ⚠️'}

🗄️  Database Configuration:
   • Host: {self.database.host}
   • Port: {self.database.port}
   • User: {self.database.user}
   • Default DB: {self.database.default_database}

🐳 Docker Configuration:
   • Compose File: {self.docker.compose_file}
   • Odoo Service: {self.docker.odoo_service}
   • Command: {' '.join(self.docker.get_compose_command())}

📁 Path Configuration:
   • Addons: {self.paths.odoo_addons_path}
   • Backups: {self.paths.backup_path}
   • Logs: {self.paths.log_path}

🔧 Odoo Configuration:
   • Version: {self.odoo.version}
   • HTTP Port: {self.odoo.http_port}
   • Workers: {self.odoo.workers}
   • URL: {self.odoo.get_odoo_url()}

📊 Performance:
   • Caching: {'Enabled' if self.performance.enable_caching else 'Disabled'}
   • Async Subprocess: {'Enabled' if self.performance.subprocess_use_async else 'Disabled'}
   • Connection Pooling: {'Enabled' if self.performance.enable_connection_pooling else 'Disabled'}

🔒 Security:
   • Input Validation: {'Enabled' if self.security.enable_input_validation else 'Disabled'}
   • Command Whitelist: {'Enabled' if self.security.enable_command_whitelist else 'Disabled'}
   • Max Timeout: {self.security.max_subprocess_timeout}s

📋 Logging:
   • Level: {self.logging.level}
   • File: {self.logging.file or 'Console only'}
"""
        return summary


# Global configuration instance
_config: Optional[Config] = None


def get_config(reload: bool = False) -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None or reload:
        _config = Config()
    return _config


def init_config(env_file: Optional[str] = None) -> Config:
    """Initialize configuration with custom .env file."""
    global _config
    _config = Config(env_file=env_file)
    return _config


# Example usage and testing
if __name__ == "__main__":
    # Test configuration loading
    config = get_config()
    print(config.print_summary())

    print("\n🧪 Configuration Tests:")
    print(f"✅ Database connection string: {config.database.get_connection_string()}")
    print(f"✅ Docker compose command: {' '.join(config.docker.get_compose_command())}")
    print(f"✅ Backup directory: {config.paths.ensure_backup_dir()}")
    print(f"✅ Odoo URL: {config.odoo.get_odoo_url()}")
    print(f"✅ Log level: {config.logging.get_log_level()}")
