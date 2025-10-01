"""
Odoo 17 MCP Server - Security Module

This module provides security utilities including:
- Input validation and sanitization
- SQL injection prevention
- Command injection prevention
- Path traversal prevention
- Credential management
- Security policy enforcement
"""

import re
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import hashlib
import secrets
import base64
from dataclasses import dataclass

from exceptions import (
    DangerousOperationError,
    InvalidInputError,
    SecurityError,
    PermissionError as MCPPermissionError
)


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    enable_input_validation: bool = True
    max_query_length: int = 10000
    max_path_length: int = 4096
    max_command_length: int = 10000
    allowed_sql_keywords: List[str] = None
    blocked_sql_keywords: List[str] = None
    allowed_shell_commands: List[str] = None
    allow_shell_metacharacters: bool = False
    max_subprocess_timeout: int = 300

    def __post_init__(self):
        if self.allowed_sql_keywords is None:
            self.allowed_sql_keywords = ['SELECT']

        if self.blocked_sql_keywords is None:
            self.blocked_sql_keywords = [
                'DROP', 'DELETE', 'TRUNCATE', 'UPDATE', 'INSERT',
                'ALTER', 'CREATE', 'GRANT', 'REVOKE', 'EXEC', 'EXECUTE'
            ]

        if self.allowed_shell_commands is None:
            self.allowed_shell_commands = [
                'docker', 'docker-compose', 'git', 'pip', 'python',
                'pytest', 'flake8', 'pylint', 'black', 'isort', 'psql',
                'pg_dump', 'pg_restore', 'createdb', 'dropdb'
            ]


class InputValidator:
    """Validates and sanitizes user inputs."""

    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy or SecurityPolicy()

    def validate_module_name(self, name: str) -> str:
        """
        Validate Odoo module name format.

        Args:
            name: Module name to validate

        Returns:
            Validated module name

        Raises:
            InvalidInputError: If name is invalid
        """
        if not name:
            raise InvalidInputError("module_name", "Module name cannot be empty")

        # Odoo module names must be lowercase, alphanumeric with underscores
        if not re.match(r'^[a-z][a-z0-9_]*$', name):
            raise InvalidInputError(
                "module_name",
                "Module name must start with lowercase letter and contain only lowercase letters, numbers, and underscores"
            )

        if len(name) > 100:
            raise InvalidInputError("module_name", "Module name too long (max 100 characters)")

        # Reserved Python keywords that can't be used
        python_keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del',
            'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if',
            'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass',
            'raise', 'return', 'try', 'while', 'with', 'yield'
        ]

        if name in python_keywords:
            raise InvalidInputError("module_name", f"Cannot use Python keyword '{name}' as module name")

        return name

    def validate_path(
        self,
        path: Union[str, Path],
        must_exist: bool = False,
        must_be_dir: bool = False,
        must_be_file: bool = False,
        allowed_extensions: Optional[List[str]] = None,
        base_path: Optional[Path] = None
    ) -> Path:
        """
        Validate file system path with security checks.

        Args:
            path: Path to validate
            must_exist: Path must exist
            must_be_dir: Path must be a directory
            must_be_file: Path must be a file
            allowed_extensions: List of allowed file extensions
            base_path: Base path to prevent traversal attacks

        Returns:
            Validated Path object

        Raises:
            InvalidInputError: If path is invalid
            SecurityError: If path traversal detected
        """
        if not path:
            raise InvalidInputError("path", "Path cannot be empty")

        path_obj = Path(path)

        # Check for path traversal attempts
        path_str = str(path_obj)
        if '..' in path_str or path_str.startswith('/'):
            if base_path:
                # Resolve and check if within base_path
                try:
                    resolved = path_obj.resolve()
                    base_resolved = base_path.resolve()
                    if not str(resolved).startswith(str(base_resolved)):
                        raise SecurityError("Path traversal attack detected")
                except Exception:
                    raise SecurityError("Invalid path resolution")

        # Check path length
        if len(str(path_obj)) > self.policy.max_path_length:
            raise InvalidInputError("path", f"Path too long (max {self.policy.max_path_length} characters)")

        # Check existence
        if must_exist and not path_obj.exists():
            raise InvalidInputError("path", f"Path does not exist: {path_obj}")

        # Check type
        if must_be_dir and path_obj.exists() and not path_obj.is_dir():
            raise InvalidInputError("path", f"Path must be a directory: {path_obj}")

        if must_be_file and path_obj.exists() and not path_obj.is_file():
            raise InvalidInputError("path", f"Path must be a file: {path_obj}")

        # Check extension
        if allowed_extensions and path_obj.suffix:
            if path_obj.suffix.lower() not in allowed_extensions:
                raise InvalidInputError(
                    "path",
                    f"File extension '{path_obj.suffix}' not allowed. Allowed: {allowed_extensions}"
                )

        return path_obj

    def validate_database_name(self, name: str) -> str:
        """
        Validate PostgreSQL database name.

        Args:
            name: Database name to validate

        Returns:
            Validated database name

        Raises:
            InvalidInputError: If name is invalid
        """
        if not name:
            raise InvalidInputError("database", "Database name cannot be empty")

        # PostgreSQL naming rules
        if not re.match(r'^[a-z_][a-z0-9_]*$', name):
            raise InvalidInputError(
                "database",
                "Database name must start with letter or underscore and contain only lowercase letters, numbers, and underscores"
            )

        if len(name) > 63:
            raise InvalidInputError("database", "Database name too long (max 63 characters)")

        # Reserved names
        reserved = ['postgres', 'template0', 'template1']
        if name.lower() in reserved:
            raise InvalidInputError("database", f"Cannot use reserved database name: {name}")

        return name

    def validate_sql_query(self, query: str) -> str:
        """
        Validate SQL query for safety.

        Args:
            query: SQL query to validate

        Returns:
            Validated query

        Raises:
            DangerousOperationError: If query contains dangerous operations
        """
        if not query:
            raise InvalidInputError("query", "Query cannot be empty")

        if len(query) > self.policy.max_query_length:
            raise InvalidInputError("query", f"Query too long (max {self.policy.max_query_length} characters)")

        query_upper = query.strip().upper()

        # Check for dangerous keywords
        for keyword in self.policy.blocked_sql_keywords:
            # Match keyword at start or after whitespace
            if re.search(r'(^|\s)' + keyword + r'(\s|$)', query_upper):
                raise DangerousOperationError(
                    f"SQL query contains blocked keyword: {keyword}",
                    "Only SELECT queries are allowed for safety"
                )

        # Ensure query starts with allowed keyword
        starts_with_allowed = False
        for keyword in self.policy.allowed_sql_keywords:
            if query_upper.startswith(keyword):
                starts_with_allowed = True
                break

        if not starts_with_allowed:
            raise DangerousOperationError(
                "SQL query must start with an allowed keyword",
                f"Allowed keywords: {', '.join(self.policy.allowed_sql_keywords)}"
            )

        # Check for SQL injection patterns
        injection_patterns = [
            r";\s*DROP",
            r";\s*DELETE",
            r"--\s*$",  # SQL comments at end
            r"/\*.*\*/",  # Multi-line comments
            r"UNION\s+SELECT",
            r"OR\s+1\s*=\s*1",
            r"OR\s+'1'\s*=\s*'1'"
        ]

        for pattern in injection_patterns:
            if re.search(pattern, query_upper):
                raise DangerousOperationError(
                    "Potential SQL injection detected",
                    f"Query matches dangerous pattern: {pattern}"
                )

        return query

    def validate_shell_command(self, command: Union[str, List[str]]) -> List[str]:
        """
        Validate shell command for safety.

        Args:
            command: Command string or list to validate

        Returns:
            Validated command as list

        Raises:
            DangerousOperationError: If command is dangerous
            InvalidInputError: If command format is invalid
        """
        if not command:
            raise InvalidInputError("command", "Command cannot be empty")

        # Convert to list if string
        if isinstance(command, str):
            # Simple split - better to use shlex.split but for security we keep it simple
            cmd_list = command.split()
        else:
            cmd_list = list(command)

        if not cmd_list:
            raise InvalidInputError("command", "Command list cannot be empty")

        # Get base command
        base_command = cmd_list[0].lower()

        # Remove path if present (e.g., /usr/bin/docker -> docker)
        if '/' in base_command or '\\' in base_command:
            base_command = Path(base_command).name

        # Check if command is in whitelist
        if self.policy.allowed_shell_commands:
            if base_command not in [c.lower() for c in self.policy.allowed_shell_commands]:
                raise DangerousOperationError(
                    f"Command not in whitelist: {base_command}",
                    f"Allowed commands: {', '.join(self.policy.allowed_shell_commands)}"
                )

        # Check for shell metacharacters if not allowed
        if not self.policy.allow_shell_metacharacters:
            dangerous_chars = ['|', '&', ';', '>', '<', '`', '$', '(', ')']
            command_str = ' '.join(cmd_list)

            for char in dangerous_chars:
                if char in command_str:
                    raise DangerousOperationError(
                        f"Shell metacharacter detected: {char}",
                        "Shell metacharacters are not allowed for security"
                    )

        # Check total command length
        total_length = sum(len(arg) for arg in cmd_list)
        if total_length > self.policy.max_command_length:
            raise InvalidInputError("command", f"Command too long (max {self.policy.max_command_length} characters)")

        return cmd_list

    def validate_email(self, email: str) -> str:
        """Validate email address format."""
        if not email:
            raise InvalidInputError("email", "Email cannot be empty")

        # Simple email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise InvalidInputError("email", "Invalid email format")

        if len(email) > 254:
            raise InvalidInputError("email", "Email too long (max 254 characters)")

        return email.lower()

    def validate_url(self, url: str, allowed_schemes: Optional[List[str]] = None) -> str:
        """Validate URL format."""
        if not url:
            raise InvalidInputError("url", "URL cannot be empty")

        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']

        # Basic URL validation
        url_pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, url, re.IGNORECASE):
            raise InvalidInputError("url", "Invalid URL format")

        # Check scheme
        scheme = url.split('://')[0].lower()
        if scheme not in allowed_schemes:
            raise InvalidInputError("url", f"URL scheme not allowed. Allowed: {allowed_schemes}")

        if len(url) > 2048:
            raise InvalidInputError("url", "URL too long (max 2048 characters)")

        return url

    def sanitize_string(self, value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize string input.

        Args:
            value: String to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)

        # Remove null bytes
        value = value.replace('\x00', '')

        # Remove control characters except newlines and tabs
        value = ''.join(char for char in value if char >= ' ' or char in '\n\t\r')

        # Truncate if too long
        if max_length and len(value) > max_length:
            value = value[:max_length]

        return value.strip()


class CredentialManager:
    """Secure credential storage and retrieval."""

    def __init__(self):
        self._credentials: Dict[str, bytes] = {}
        self._salt = self._generate_salt()

    def _generate_salt(self) -> bytes:
        """Generate a random salt."""
        return secrets.token_bytes(32)

    def _hash_key(self, key: str) -> str:
        """Hash a key for storage."""
        return hashlib.sha256((key + base64.b64encode(self._salt).decode()).encode()).hexdigest()

    def _encrypt_value(self, value: str) -> bytes:
        """Simple XOR encryption (for basic obfuscation, not cryptographically secure)."""
        # Note: In production, use proper encryption like Fernet from cryptography library
        key_bytes = self._salt
        value_bytes = value.encode('utf-8')

        encrypted = bytearray()
        for i, byte in enumerate(value_bytes):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])

        return bytes(encrypted)

    def _decrypt_value(self, encrypted: bytes) -> str:
        """Decrypt XOR encrypted value."""
        key_bytes = self._salt
        decrypted = bytearray()

        for i, byte in enumerate(encrypted):
            decrypted.append(byte ^ key_bytes[i % len(key_bytes)])

        return decrypted.decode('utf-8')

    def store(self, key: str, value: str) -> None:
        """
        Store a credential securely.

        Args:
            key: Credential key/name
            value: Credential value
        """
        hashed_key = self._hash_key(key)
        encrypted_value = self._encrypt_value(value)
        self._credentials[hashed_key] = encrypted_value

    def retrieve(self, key: str) -> Optional[str]:
        """
        Retrieve a stored credential.

        Args:
            key: Credential key/name

        Returns:
            Decrypted credential value or None if not found
        """
        hashed_key = self._hash_key(key)
        encrypted_value = self._credentials.get(hashed_key)

        if encrypted_value is None:
            return None

        return self._decrypt_value(encrypted_value)

    def delete(self, key: str) -> bool:
        """
        Delete a stored credential.

        Args:
            key: Credential key/name

        Returns:
            True if deleted, False if not found
        """
        hashed_key = self._hash_key(key)
        if hashed_key in self._credentials:
            del self._credentials[hashed_key]
            return True
        return False

    def clear(self) -> None:
        """Clear all stored credentials."""
        self._credentials.clear()


class SecurityManager:
    """Main security manager combining all security features."""

    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy or SecurityPolicy()
        self.validator = InputValidator(self.policy)
        self.credentials = CredentialManager()

    def check_file_permissions(self, path: Path, required_mode: str = 'r') -> bool:
        """
        Check if file has required permissions.

        Args:
            path: File path to check
            required_mode: Required mode ('r', 'w', 'x')

        Returns:
            True if has permission

        Raises:
            MCPPermissionError: If permission denied
        """
        if not path.exists():
            raise MCPPermissionError(str(path), "access", reason="File does not exist")

        if required_mode == 'r':
            if not os.access(path, os.R_OK):
                raise MCPPermissionError(str(path), "read")
        elif required_mode == 'w':
            if not os.access(path, os.W_OK):
                raise MCPPermissionError(str(path), "write")
        elif required_mode == 'x':
            if not os.access(path, os.X_OK):
                raise MCPPermissionError(str(path), "execute")

        return True

    def sanitize_for_log(self, message: str, secrets_to_hide: Optional[List[str]] = None) -> str:
        """
        Sanitize message for logging by hiding secrets.

        Args:
            message: Message to sanitize
            secrets_to_hide: List of secret strings to hide

        Returns:
            Sanitized message
        """
        if secrets_to_hide:
            for secret in secrets_to_hide:
                if secret and len(secret) > 3:
                    message = message.replace(secret, '***HIDDEN***')

        # Hide common patterns (passwords, tokens, keys)
        patterns = [
            (r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)["\']?', 'password=***HIDDEN***'),
            (r'token["\']?\s*[:=]\s*["\']?([^"\'\s]+)["\']?', 'token=***HIDDEN***'),
            (r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'\s]+)["\']?', 'api_key=***HIDDEN***'),
            (r'secret["\']?\s*[:=]\s*["\']?([^"\'\s]+)["\']?', 'secret=***HIDDEN***'),
        ]

        for pattern, replacement in patterns:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)

        return message


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager(policy: Optional[SecurityPolicy] = None) -> SecurityManager:
    """Get global security manager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager(policy)
    return _security_manager


# Testing
if __name__ == "__main__":
    # Test input validation
    security = get_security_manager()

    print("Testing module name validation...")
    try:
        print(f"✅ Valid: {security.validator.validate_module_name('my_module')}")
        print(f"❌ Invalid: {security.validator.validate_module_name('MyModule')}")
    except Exception as e:
        print(f"❌ {e}")

    print("\nTesting SQL validation...")
    try:
        print(f"✅ Valid: {security.validator.validate_sql_query('SELECT * FROM users LIMIT 10')}")
        print(f"❌ Invalid: {security.validator.validate_sql_query('DROP TABLE users')}")
    except Exception as e:
        print(f"❌ {e}")

    print("\nTesting credential storage...")
    security.credentials.store('db_password', 'super_secret_123')
    print(f"✅ Stored and retrieved: {security.credentials.retrieve('db_password')}")
    print(f"✅ Sanitized log: {security.sanitize_for_log('password=super_secret_123')}")
