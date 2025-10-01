"""
Odoo 17 MCP Server - Async Utilities

This module provides async utilities for non-blocking operations including:
- Async subprocess execution
- Process timeout handling
- Retry logic with exponential backoff
- Cross-platform command execution
- Error handling and logging
"""

import asyncio
import logging
import platform
import shlex
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any, Callable
from dataclasses import dataclass
from functools import wraps
import time

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of a command execution."""
    returncode: int
    stdout: str
    stderr: str
    command: str
    duration: float
    success: bool

    def __str__(self) -> str:
        status = "✅ SUCCESS" if self.success else f"❌ FAILED (exit code: {self.returncode})"
        return f"{status} | Command: {self.command} | Duration: {self.duration:.2f}s"


class AsyncCommandExecutor:
    """Execute commands asynchronously with proper error handling and retries."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.is_windows = platform.system() == "Windows"

    async def run(
        self,
        command: List[str],
        timeout: Optional[float] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        input_data: Optional[str] = None,
        capture_output: bool = True,
        shell: bool = False
    ) -> CommandResult:
        """
        Execute a command asynchronously.

        Args:
            command: Command and arguments as list
            timeout: Timeout in seconds (None for no timeout)
            cwd: Working directory
            env: Environment variables
            input_data: Data to send to stdin
            capture_output: Whether to capture stdout/stderr
            shell: Whether to use shell execution

        Returns:
            CommandResult with execution details
        """
        start_time = time.time()
        cmd_str = ' '.join(command) if isinstance(command, list) else command

        try:
            self.logger.debug(f"Executing command: {cmd_str}")

            # Create subprocess
            if shell:
                process = await asyncio.create_subprocess_shell(
                    cmd_str,
                    stdout=asyncio.subprocess.PIPE if capture_output else None,
                    stderr=asyncio.subprocess.PIPE if capture_output else None,
                    stdin=asyncio.subprocess.PIPE if input_data else None,
                    cwd=cwd,
                    env=env
                )
            else:
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE if capture_output else None,
                    stderr=asyncio.subprocess.PIPE if capture_output else None,
                    stdin=asyncio.subprocess.PIPE if input_data else None,
                    cwd=cwd,
                    env=env
                )

            # Communicate with timeout
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(input=input_data.encode() if input_data else None),
                    timeout=timeout
                )

                stdout = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ''
                stderr = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ''
                returncode = process.returncode

            except asyncio.TimeoutError:
                # Kill the process on timeout
                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass

                duration = time.time() - start_time
                self.logger.error(f"Command timed out after {timeout}s: {cmd_str}")

                return CommandResult(
                    returncode=-1,
                    stdout='',
                    stderr=f'Command timed out after {timeout} seconds',
                    command=cmd_str,
                    duration=duration,
                    success=False
                )

            duration = time.time() - start_time
            success = returncode == 0

            if not success:
                self.logger.warning(f"Command failed: {cmd_str} (exit code: {returncode})")
            else:
                self.logger.debug(f"Command succeeded: {cmd_str} ({duration:.2f}s)")

            return CommandResult(
                returncode=returncode,
                stdout=stdout,
                stderr=stderr,
                command=cmd_str,
                duration=duration,
                success=success
            )

        except FileNotFoundError:
            duration = time.time() - start_time
            error_msg = f"Command not found: {command[0] if isinstance(command, list) else command}"
            self.logger.error(error_msg)

            return CommandResult(
                returncode=-1,
                stdout='',
                stderr=error_msg,
                command=cmd_str,
                duration=duration,
                success=False
            )

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Error executing command: {str(e)}"
            self.logger.error(f"{error_msg} | Command: {cmd_str}")

            return CommandResult(
                returncode=-1,
                stdout='',
                stderr=error_msg,
                command=cmd_str,
                duration=duration,
                success=False
            )

    async def run_with_retry(
        self,
        command: List[str],
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        **kwargs
    ) -> CommandResult:
        """
        Execute a command with retry logic and exponential backoff.

        Args:
            command: Command and arguments
            max_retries: Maximum number of retries
            retry_delay: Initial delay between retries in seconds
            backoff_factor: Multiplier for delay after each retry
            **kwargs: Additional arguments passed to run()

        Returns:
            CommandResult from the last attempt
        """
        last_result = None
        delay = retry_delay

        for attempt in range(max_retries + 1):
            if attempt > 0:
                self.logger.info(f"Retry attempt {attempt}/{max_retries} after {delay:.1f}s delay")
                await asyncio.sleep(delay)
                delay *= backoff_factor

            result = await self.run(command, **kwargs)

            if result.success:
                if attempt > 0:
                    self.logger.info(f"Command succeeded on attempt {attempt + 1}")
                return result

            last_result = result

        self.logger.error(f"Command failed after {max_retries + 1} attempts")
        return last_result

    async def run_multiple(
        self,
        commands: List[List[str]],
        parallel: bool = False,
        stop_on_error: bool = False,
        **kwargs
    ) -> List[CommandResult]:
        """
        Execute multiple commands either sequentially or in parallel.

        Args:
            commands: List of commands to execute
            parallel: Execute commands in parallel if True
            stop_on_error: Stop execution if a command fails (sequential only)
            **kwargs: Additional arguments passed to run()

        Returns:
            List of CommandResults
        """
        if parallel:
            # Run all commands concurrently
            tasks = [self.run(cmd, **kwargs) for cmd in commands]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to error results
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    final_results.append(CommandResult(
                        returncode=-1,
                        stdout='',
                        stderr=str(result),
                        command=' '.join(commands[i]),
                        duration=0.0,
                        success=False
                    ))
                else:
                    final_results.append(result)

            return final_results
        else:
            # Run commands sequentially
            results = []
            for cmd in commands:
                result = await self.run(cmd, **kwargs)
                results.append(result)

                if stop_on_error and not result.success:
                    self.logger.warning(f"Stopping execution due to failure: {result.command}")
                    break

            return results


class DockerCommandBuilder:
    """Build Docker and Docker Compose commands with cross-platform support."""

    def __init__(self, use_compose_v2: bool = True):
        self.use_compose_v2 = use_compose_v2
        self.is_windows = platform.system() == "Windows"

    def compose_base(self, compose_file: Optional[str] = None) -> List[str]:
        """Get base docker compose command."""
        if self.use_compose_v2:
            cmd = ['docker', 'compose']
        else:
            cmd = ['docker-compose']

        if compose_file and compose_file != "docker-compose.yml":
            cmd.extend(['-f', compose_file])

        return cmd

    def compose_up(self, services: Optional[List[str]] = None, detached: bool = True, **kwargs) -> List[str]:
        """Build 'docker compose up' command."""
        cmd = self.compose_base(kwargs.get('compose_file'))
        cmd.append('up')

        if detached:
            cmd.append('-d')

        if services:
            cmd.extend(services)

        return cmd

    def compose_down(self, volumes: bool = False, **kwargs) -> List[str]:
        """Build 'docker compose down' command."""
        cmd = self.compose_base(kwargs.get('compose_file'))
        cmd.append('down')

        if volumes:
            cmd.append('-v')

        return cmd

    def compose_restart(self, services: Optional[List[str]] = None, **kwargs) -> List[str]:
        """Build 'docker compose restart' command."""
        cmd = self.compose_base(kwargs.get('compose_file'))
        cmd.append('restart')

        if services:
            cmd.extend(services)

        return cmd

    def compose_logs(
        self,
        service: str,
        follow: bool = False,
        tail: Optional[int] = None,
        **kwargs
    ) -> List[str]:
        """Build 'docker compose logs' command."""
        cmd = self.compose_base(kwargs.get('compose_file'))
        cmd.append('logs')

        if follow:
            cmd.append('-f')

        if tail is not None:
            cmd.extend(['--tail', str(tail)])

        cmd.append(service)

        return cmd

    def compose_exec(
        self,
        service: str,
        command: List[str],
        interactive: bool = False,
        **kwargs
    ) -> List[str]:
        """Build 'docker compose exec' command."""
        cmd = self.compose_base(kwargs.get('compose_file'))
        cmd.append('exec')

        if not interactive:
            cmd.append('-T')

        cmd.append(service)
        cmd.extend(command)

        return cmd

    def compose_ps(self, **kwargs) -> List[str]:
        """Build 'docker compose ps' command."""
        cmd = self.compose_base(kwargs.get('compose_file'))
        cmd.append('ps')
        return cmd


def retry_async(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple = (Exception,)
):
    """
    Decorator for retrying async functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries + 1} attempts: {e}")
                        raise

                    logger.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

        return wrapper
    return decorator


async def timeout_async(coro, timeout: float, default=None):
    """
    Run a coroutine with a timeout.

    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds
        default: Default value to return on timeout

    Returns:
        Result of coroutine or default value on timeout
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout}s")
        return default


class AsyncCache:
    """Simple async-safe cache with TTL support."""

    def __init__(self, ttl: int = 300, max_size: int = 1000):
        self.ttl = ttl
        self.max_size = max_size
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                else:
                    # Expired
                    del self._cache[key]
            return None

    async def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        async with self._lock:
            # Evict oldest if cache is full
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
                del self._cache[oldest_key]

            self._cache[key] = (value, time.time())

    async def clear(self) -> None:
        """Clear all cached values."""
        async with self._lock:
            self._cache.clear()

    async def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]


# Global instances
_executor: Optional[AsyncCommandExecutor] = None
_docker_builder: Optional[DockerCommandBuilder] = None
_cache: Optional[AsyncCache] = None


def get_executor() -> AsyncCommandExecutor:
    """Get global command executor instance."""
    global _executor
    if _executor is None:
        _executor = AsyncCommandExecutor()
    return _executor


def get_docker_builder(use_compose_v2: bool = True) -> DockerCommandBuilder:
    """Get global Docker command builder instance."""
    global _docker_builder
    if _docker_builder is None:
        _docker_builder = DockerCommandBuilder(use_compose_v2=use_compose_v2)
    return _docker_builder


def get_cache(ttl: int = 300, max_size: int = 1000) -> AsyncCache:
    """Get global cache instance."""
    global _cache
    if _cache is None:
        _cache = AsyncCache(ttl=ttl, max_size=max_size)
    return _cache


# Testing
if __name__ == "__main__":
    async def test_executor():
        executor = AsyncCommandExecutor()

        # Test simple command
        print("Testing simple command...")
        result = await executor.run(['echo', 'Hello, World!'])
        print(result)

        # Test command with timeout
        print("\nTesting command with timeout...")
        if platform.system() == "Windows":
            result = await executor.run(['ping', '-n', '10', 'localhost'], timeout=2.0)
        else:
            result = await executor.run(['sleep', '10'], timeout=2.0)
        print(result)

        # Test retry logic
        print("\nTesting retry logic...")
        result = await executor.run_with_retry(['python', '--version'], max_retries=2)
        print(result)

        # Test parallel execution
        print("\nTesting parallel execution...")
        commands = [
            ['echo', 'Command 1'],
            ['echo', 'Command 2'],
            ['echo', 'Command 3']
        ]
        results = await executor.run_multiple(commands, parallel=True)
        for r in results:
            print(r)

    asyncio.run(test_executor())
