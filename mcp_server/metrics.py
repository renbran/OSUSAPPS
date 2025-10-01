"""
Odoo 17 MCP Server - Metrics and Monitoring

This module provides:
- Tool usage tracking and statistics
- Performance metrics collection
- Error tracking and analysis
- Resource usage monitoring
- Metrics export and reporting
"""

import time
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolMetrics:
    """Metrics for a single tool execution."""
    tool_name: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    result_size: int = 0  # Size of result in characters/bytes

    @property
    def timestamp(self) -> str:
        """Get formatted timestamp."""
        return datetime.fromtimestamp(self.start_time).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'tool_name': self.tool_name,
            'timestamp': self.timestamp,
            'duration': self.duration,
            'success': self.success,
            'error_type': self.error_type,
            'error_message': self.error_message,
            'result_size': self.result_size
        }


@dataclass
class ToolStatistics:
    """Aggregated statistics for a tool."""
    tool_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    avg_duration: float = 0.0
    error_count: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_used: Optional[str] = None

    def update(self, metrics: ToolMetrics) -> None:
        """Update statistics with new metrics."""
        self.total_calls += 1

        if metrics.success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
            if metrics.error_type:
                self.error_count[metrics.error_type] += 1

        self.total_duration += metrics.duration
        self.min_duration = min(self.min_duration, metrics.duration)
        self.max_duration = max(self.max_duration, metrics.duration)
        self.avg_duration = self.total_duration / self.total_calls
        self.last_used = metrics.timestamp

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'tool_name': self.tool_name,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'success_rate': f"{self.success_rate:.2f}%",
            'avg_duration': f"{self.avg_duration:.3f}s",
            'min_duration': f"{self.min_duration:.3f}s",
            'max_duration': f"{self.max_duration:.3f}s",
            'top_errors': dict(sorted(
                self.error_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            'last_used': self.last_used
        }


class MetricsCollector:
    """Collects and manages metrics for all tools."""

    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self._metrics_history: deque = deque(maxlen=max_history)
        self._tool_stats: Dict[str, ToolStatistics] = {}
        self._session_start = time.time()
        self.logger = logger

    def record_tool_execution(
        self,
        tool_name: str,
        start_time: float,
        end_time: float,
        success: bool,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        result_size: int = 0
    ) -> ToolMetrics:
        """
        Record a tool execution.

        Args:
            tool_name: Name of the tool
            start_time: Start timestamp
            end_time: End timestamp
            success: Whether execution was successful
            error_type: Type of error if failed
            error_message: Error message if failed
            parameters: Tool parameters
            result_size: Size of result

        Returns:
            ToolMetrics instance
        """
        duration = end_time - start_time

        metrics = ToolMetrics(
            tool_name=tool_name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            success=success,
            error_type=error_type,
            error_message=error_message,
            parameters=parameters or {},
            result_size=result_size
        )

        # Add to history
        self._metrics_history.append(metrics)

        # Update statistics
        if tool_name not in self._tool_stats:
            self._tool_stats[tool_name] = ToolStatistics(tool_name=tool_name)

        self._tool_stats[tool_name].update(metrics)

        self.logger.debug(
            f"Recorded metrics for {tool_name}: "
            f"duration={duration:.3f}s, success={success}"
        )

        return metrics

    def get_tool_statistics(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a specific tool or all tools.

        Args:
            tool_name: Tool name, or None for all tools

        Returns:
            Dictionary of statistics
        """
        if tool_name:
            stats = self._tool_stats.get(tool_name)
            return stats.to_dict() if stats else {}
        else:
            return {
                name: stats.to_dict()
                for name, stats in self._tool_stats.items()
            }

    def get_recent_executions(
        self,
        count: int = 100,
        tool_name: Optional[str] = None,
        only_failures: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get recent tool executions.

        Args:
            count: Number of executions to return
            tool_name: Filter by tool name
            only_failures: Only return failed executions

        Returns:
            List of execution metrics
        """
        filtered = self._metrics_history

        if tool_name:
            filtered = [m for m in filtered if m.tool_name == tool_name]

        if only_failures:
            filtered = [m for m in filtered if not m.success]

        return [m.to_dict() for m in list(filtered)[-count:]]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get overall metrics summary.

        Returns:
            Dictionary with summary statistics
        """
        total_executions = len(self._metrics_history)
        successful = sum(1 for m in self._metrics_history if m.success)
        failed = total_executions - successful

        session_duration = time.time() - self._session_start

        # Calculate overall statistics
        if total_executions > 0:
            total_duration = sum(m.duration for m in self._metrics_history)
            avg_duration = total_duration / total_executions
            success_rate = (successful / total_executions) * 100
        else:
            avg_duration = 0.0
            success_rate = 0.0

        # Top tools by usage
        tool_usage = defaultdict(int)
        for m in self._metrics_history:
            tool_usage[m.tool_name] += 1

        top_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:10]

        # Error distribution
        error_distribution = defaultdict(int)
        for m in self._metrics_history:
            if m.error_type:
                error_distribution[m.error_type] += 1

        return {
            'session_duration': f"{session_duration:.1f}s",
            'total_executions': total_executions,
            'successful_executions': successful,
            'failed_executions': failed,
            'success_rate': f"{success_rate:.2f}%",
            'average_duration': f"{avg_duration:.3f}s",
            'unique_tools_used': len(self._tool_stats),
            'top_tools': [
                {'tool': tool, 'count': count}
                for tool, count in top_tools
            ],
            'error_distribution': dict(error_distribution),
            'metrics_history_size': len(self._metrics_history)
        }

    def get_performance_report(self) -> str:
        """Generate a formatted performance report."""
        summary = self.get_summary()

        report = [
            "=" * 70,
            "Odoo 17 MCP Server - Performance Report",
            "=" * 70,
            "",
            f"📊 Session Duration: {summary['session_duration']}",
            f"📈 Total Executions: {summary['total_executions']}",
            f"✅ Successful: {summary['successful_executions']}",
            f"❌ Failed: {summary['failed_executions']}",
            f"📊 Success Rate: {summary['success_rate']}",
            f"⏱️  Average Duration: {summary['average_duration']}",
            f"🔧 Unique Tools Used: {summary['unique_tools_used']}",
            "",
            "🔝 Top Tools by Usage:",
        ]

        for item in summary['top_tools']:
            report.append(f"   {item['count']:4d} - {item['tool']}")

        if summary['error_distribution']:
            report.extend([
                "",
                "💥 Error Distribution:",
            ])
            for error_type, count in sorted(
                summary['error_distribution'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                report.append(f"   {count:4d} - {error_type}")

        report.extend([
            "",
            "📋 Tool Statistics:",
            ""
        ])

        # Add individual tool statistics
        for tool_name, stats in sorted(self._tool_stats.items()):
            report.append(f"🔧 {tool_name}")
            report.append(f"   Calls: {stats.total_calls}")
            report.append(f"   Success Rate: {stats.success_rate:.2f}%")
            report.append(f"   Avg Duration: {stats.avg_duration:.3f}s")
            report.append(f"   Min/Max: {stats.min_duration:.3f}s / {stats.max_duration:.3f}s")
            if stats.error_count:
                top_errors = sorted(stats.error_count.items(), key=lambda x: x[1], reverse=True)[:3]
                report.append(f"   Top Errors: {', '.join(f'{e}({c})' for e, c in top_errors)}")
            report.append("")

        report.append("=" * 70)

        return "\n".join(report)

    def export_metrics(self, file_path: str) -> None:
        """
        Export metrics to JSON file.

        Args:
            file_path: Path to export file
        """
        export_data = {
            'export_time': datetime.now().isoformat(),
            'summary': self.get_summary(),
            'tool_statistics': self.get_tool_statistics(),
            'recent_executions': self.get_recent_executions(count=1000)
        }

        try:
            Path(file_path).write_text(json.dumps(export_data, indent=2))
            self.logger.info(f"Metrics exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
            raise

    def clear_history(self) -> None:
        """Clear metrics history (keeps statistics)."""
        self._metrics_history.clear()
        self.logger.info("Metrics history cleared")

    def reset(self) -> None:
        """Reset all metrics and statistics."""
        self._metrics_history.clear()
        self._tool_stats.clear()
        self._session_start = time.time()
        self.logger.info("All metrics reset")


class MetricsDecorator:
    """Decorator for automatic metrics collection."""

    def __init__(self, collector: MetricsCollector, tool_name: str):
        self.collector = collector
        self.tool_name = tool_name

    def __call__(self, func):
        """Decorate function to collect metrics."""
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error_type = None
            error_message = None
            result_size = 0

            try:
                result = await func(*args, **kwargs)
                success = True

                # Try to get result size
                if hasattr(result, 'content'):
                    result_size = sum(len(str(c)) for c in result.content)

                return result

            except Exception as e:
                error_type = type(e).__name__
                error_message = str(e)
                raise

            finally:
                end_time = time.time()
                self.collector.record_tool_execution(
                    tool_name=self.tool_name,
                    start_time=start_time,
                    end_time=end_time,
                    success=success,
                    error_type=error_type,
                    error_message=error_message,
                    parameters=kwargs,
                    result_size=result_size
                )

        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            error_type = None
            error_message = None
            result_size = 0

            try:
                result = func(*args, **kwargs)
                success = True

                if hasattr(result, 'content'):
                    result_size = sum(len(str(c)) for c in result.content)

                return result

            except Exception as e:
                error_type = type(e).__name__
                error_message = str(e)
                raise

            finally:
                end_time = time.time()
                self.collector.record_tool_execution(
                    tool_name=self.tool_name,
                    start_time=start_time,
                    end_time=end_time,
                    success=success,
                    error_type=error_type,
                    error_message=error_message,
                    parameters=kwargs,
                    result_size=result_size
                )

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector(max_history: int = 10000) -> MetricsCollector:
    """Get global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector(max_history=max_history)
    return _metrics_collector


def metrics_for_tool(tool_name: str):
    """
    Decorator to collect metrics for a tool.

    Usage:
        @metrics_for_tool("my_tool")
        async def my_tool_implementation():
            pass
    """
    collector = get_metrics_collector()
    return MetricsDecorator(collector, tool_name)


# Testing
if __name__ == "__main__":
    print("Testing Metrics System...")

    collector = MetricsCollector()

    # Simulate some tool executions
    import random

    tools = ['scaffold_module', 'validate_manifest', 'lint_code', 'docker_status']

    for i in range(50):
        tool = random.choice(tools)
        start = time.time()
        duration = random.uniform(0.1, 2.0)
        time.sleep(0.01)  # Small delay
        end = start + duration
        success = random.random() > 0.2  # 80% success rate

        collector.record_tool_execution(
            tool_name=tool,
            start_time=start,
            end_time=end,
            success=success,
            error_type="ValidationError" if not success else None,
            error_message="Sample error" if not success else None
        )

    # Print report
    print(collector.get_performance_report())

    # Export metrics
    collector.export_metrics("metrics_test.json")
    print("\n✅ Metrics exported to metrics_test.json")
