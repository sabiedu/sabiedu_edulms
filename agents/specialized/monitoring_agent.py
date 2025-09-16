"""
Monitoring Agent for EduLMS v2
Handles system monitoring, health checks, and performance tracking
"""

import asyncio
import json
import logging
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ..communication.gemini_client import get_gemini_client
from ..communication.cache_manager import CacheManager
from ..base import BaseAgent

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System metrics structure"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    active_connections: int
    response_times: Dict[str, float]
    error_rates: Dict[str, float]
    timestamp: datetime

@dataclass
class HealthCheck:
    """Health check result structure"""
    service_name: str
    status: str  # healthy, degraded, unhealthy
    response_time: float
    error_message: Optional[str]
    timestamp: datetime

class MonitoringAgent(BaseAgent):
    """
    Monitoring Agent for system health and performance tracking
    
    Capabilities:
    - System resource monitoring
    - Service health checks
    - Performance metrics collection
    - Alert generation and notification
    - Anomaly detection
    - Automated diagnostics
    """
    
    def __init__(self, agent_id: str = "monitoring_agent"):
        super().__init__(agent_id)
        self.gemini_client = get_gemini_client()
        self.cache_manager = CacheManager()
        
        # Monitoring configuration
        self.check_interval = 30  # seconds
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "response_time": 5.0,
            "error_rate": 5.0
        }
        
        # Services to monitor
        self.monitored_services = [
            {"name": "database", "url": "http://localhost:3306", "type": "database"},
            {"name": "backend", "url": "http://localhost:1337", "type": "api"},
            {"name": "frontend", "url": "http://localhost:3000", "type": "web"},
            {"name": "agents", "url": "http://localhost:8000", "type": "service"}
        ]
        
        # Metrics history
        self.metrics_history = []
        self.max_history_size = 1000
    
    async def start(self):
        """Start the monitoring agent"""
        logger.info(f"Starting Monitoring Agent {self.agent_id}")
        await super().start()
        
        # Start monitoring tasks
        monitoring_tasks = [
            asyncio.create_task(self.system_monitoring_loop()),
            asyncio.create_task(self.health_check_loop()),
            asyncio.create_task(self.performance_analysis_loop()),
            asyncio.create_task(self.alert_processing_loop())
        ]
        
        try:
            await asyncio.gather(*monitoring_tasks)
        except Exception as e:
            logger.error(f"Error in monitoring agent: {e}")
        finally:
            for task in monitoring_tasks:
                if not task.done():
                    task.cancel()
    
    async def system_monitoring_loop(self):
        """Main system monitoring loop"""
        while self.running:
            try:
                # Collect system metrics
                metrics = await self.collect_system_metrics()
                
                # Store metrics
                await self.store_metrics(metrics)
                
                # Check for threshold violations
                alerts = await self.check_thresholds(metrics)
                
                # Process alerts
                for alert in alerts:
                    await self.process_alert(alert)
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in system monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def health_check_loop(self):
        """Service health check loop"""
        while self.running:
            try:
                health_results = []
                
                for service in self.monitored_services:
                    health_check = await self.perform_health_check(service)
                    health_results.append(health_check)
                
                # Store health check results
                await self.store_health_checks(health_results)
                
                # Check for service issues
                for health_check in health_results:
                    if health_check.status != "healthy":
                        await self.handle_service_issue(health_check)
                
                await asyncio.sleep(60)  # Health checks every minute
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(120)
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # Active connections (approximate)
            connections = len(psutil.net_connections())
            
            # Response times (would be collected from actual service calls)
            response_times = await self.measure_response_times()
            
            # Error rates (would be collected from logs/metrics)
            error_rates = await self.calculate_error_rates()
            
            return SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                active_connections=connections,
                response_times=response_times,
                error_rates=error_rates,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                active_connections=0,
                response_times={},
                error_rates={},
                timestamp=datetime.now()
            )
    
    async def measure_response_times(self) -> Dict[str, float]:
        """Measure response times for key endpoints"""
        response_times = {}
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                for service in self.monitored_services:
                    if service["type"] in ["api", "web"]:
                        start_time = time.time()
                        try:
                            async with session.get(service["url"], timeout=10) as response:
                                response_time = (time.time() - start_time) * 1000  # ms
                                response_times[service["name"]] = response_time
                        except Exception as e:
                            response_times[service["name"]] = 10000.0  # Timeout value
                            
        except ImportError:
            # Fallback if aiohttp not available
            response_times = {service["name"]: 100.0 for service in self.monitored_services}
        except Exception as e:
            logger.error(f"Error measuring response times: {e}")
            response_times = {}
        
        return response_times
    
    async def calculate_error_rates(self) -> Dict[str, float]:
        """Calculate error rates for services"""
        # This would typically read from logs or metrics databases
        # For now, return mock data
        return {
            "database": 0.1,
            "backend": 0.5,
            "frontend": 0.2,
            "agents": 0.3
        }
    
    async def perform_health_check(self, service: Dict[str, Any]) -> HealthCheck:
        """Perform health check on a service"""
        start_time = time.time()
        
        try:
            if service["type"] == "database":
                # Database health check
                status = await self.check_database_health(service)
            elif service["type"] in ["api", "web", "service"]:
                # HTTP health check
                status = await self.check_http_health(service)
            else:
                status = "unknown"
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                service_name=service["name"],
                status=status,
                response_time=response_time,
                error_message=None,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                service_name=service["name"],
                status="unhealthy",
                response_time=response_time,
                error_message=str(e),
                timestamp=datetime.now()
            )
    
    async def check_database_health(self, service: Dict[str, Any]) -> str:
        """Check database health"""
        try:
            # This would perform actual database connectivity check
            # For now, return healthy
            return "healthy"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return "unhealthy"
    
    async def check_http_health(self, service: Dict[str, Any]) -> str:
        """Check HTTP service health"""
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                health_url = f"{service['url']}/health"
                async with session.get(health_url, timeout=5) as response:
                    if response.status == 200:
                        return "healthy"
                    elif response.status < 500:
                        return "degraded"
                    else:
                        return "unhealthy"
                        
        except ImportError:
            # Fallback without aiohttp
            return "healthy"
        except Exception as e:
            logger.error(f"HTTP health check failed for {service['name']}: {e}")
            return "unhealthy"
    
    async def check_thresholds(self, metrics: SystemMetrics) -> List[Dict[str, Any]]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        # CPU usage alert
        if metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
            alerts.append({
                "type": "cpu_usage",
                "severity": "warning" if metrics.cpu_usage < 95 else "critical",
                "message": f"High CPU usage: {metrics.cpu_usage:.1f}%",
                "value": metrics.cpu_usage,
                "threshold": self.alert_thresholds["cpu_usage"]
            })
        
        # Memory usage alert
        if metrics.memory_usage > self.alert_thresholds["memory_usage"]:
            alerts.append({
                "type": "memory_usage",
                "severity": "warning" if metrics.memory_usage < 95 else "critical",
                "message": f"High memory usage: {metrics.memory_usage:.1f}%",
                "value": metrics.memory_usage,
                "threshold": self.alert_thresholds["memory_usage"]
            })
        
        # Disk usage alert
        if metrics.disk_usage > self.alert_thresholds["disk_usage"]:
            alerts.append({
                "type": "disk_usage",
                "severity": "warning" if metrics.disk_usage < 98 else "critical",
                "message": f"High disk usage: {metrics.disk_usage:.1f}%",
                "value": metrics.disk_usage,
                "threshold": self.alert_thresholds["disk_usage"]
            })
        
        # Response time alerts
        for service, response_time in metrics.response_times.items():
            if response_time > self.alert_thresholds["response_time"] * 1000:  # Convert to ms
                alerts.append({
                    "type": "response_time",
                    "severity": "warning" if response_time < 10000 else "critical",
                    "message": f"Slow response time for {service}: {response_time:.0f}ms",
                    "service": service,
                    "value": response_time,
                    "threshold": self.alert_thresholds["response_time"] * 1000
                })
        
        # Error rate alerts
        for service, error_rate in metrics.error_rates.items():
            if error_rate > self.alert_thresholds["error_rate"]:
                alerts.append({
                    "type": "error_rate",
                    "severity": "warning" if error_rate < 10 else "critical",
                    "message": f"High error rate for {service}: {error_rate:.1f}%",
                    "service": service,
                    "value": error_rate,
                    "threshold": self.alert_thresholds["error_rate"]
                })
        
        return alerts
    
    async def process_alert(self, alert: Dict[str, Any]):
        """Process and handle an alert"""
        try:
            logger.warning(f"Alert: {alert['message']}")
            
            # Generate diagnostic information
            diagnostics = await self.generate_diagnostics(alert)
            
            # Store alert
            await self.store_alert(alert, diagnostics)
            
            # Send notifications if critical
            if alert["severity"] == "critical":
                await self.send_critical_alert_notification(alert, diagnostics)
            
            # Attempt automated remediation
            if alert["type"] in ["cpu_usage", "memory_usage"]:
                await self.attempt_resource_optimization(alert)
            
        except Exception as e:
            logger.error(f"Error processing alert: {e}")
    
    async def generate_diagnostics(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Generate diagnostic information for an alert using Gemini"""
        try:
            diagnostic_prompt = f"""
            Analyze this system alert and provide diagnostic information:
            
            Alert: {alert['message']}
            Type: {alert['type']}
            Severity: {alert['severity']}
            Value: {alert.get('value', 'N/A')}
            Threshold: {alert.get('threshold', 'N/A')}
            
            Provide:
            1. Possible root causes
            2. Immediate actions to take
            3. Long-term prevention strategies
            4. Related metrics to monitor
            
            Format as JSON with keys: root_causes, immediate_actions, prevention_strategies, related_metrics
            """
            
            response = await self.gemini_client.generate_content(
                prompt=diagnostic_prompt,
                system_instruction="You are a system administrator providing diagnostic analysis for monitoring alerts.",
                temperature=0.2,
                max_tokens=1000
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {
                    "root_causes": ["Analysis failed"],
                    "immediate_actions": ["Check system manually"],
                    "prevention_strategies": ["Regular monitoring"],
                    "related_metrics": ["System resources"]
                }
                
        except Exception as e:
            logger.error(f"Error generating diagnostics: {e}")
            return {"error": str(e)}
    
    async def performance_analysis_loop(self):
        """Analyze performance trends and patterns"""
        while self.running:
            try:
                # Analyze recent metrics
                if len(self.metrics_history) >= 10:
                    analysis = await self.analyze_performance_trends()
                    await self.store_performance_analysis(analysis)
                
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in performance analysis loop: {e}")
                await asyncio.sleep(600)
    
    async def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends using recent metrics"""
        try:
            recent_metrics = self.metrics_history[-60:]  # Last hour of data
            
            # Calculate trends
            cpu_trend = self.calculate_trend([m.cpu_usage for m in recent_metrics])
            memory_trend = self.calculate_trend([m.memory_usage for m in recent_metrics])
            
            # Generate insights using Gemini
            trends_data = {
                "cpu_trend": cpu_trend,
                "memory_trend": memory_trend,
                "current_cpu": recent_metrics[-1].cpu_usage,
                "current_memory": recent_metrics[-1].memory_usage,
                "timeframe": "1 hour"
            }
            
            insights = await self.generate_performance_insights(trends_data)
            
            return {
                "trends": trends_data,
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {"error": str(e)}
    
    def calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        y = values
        
        # Calculate slope
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    async def generate_performance_insights(self, trends_data: Dict[str, Any]) -> List[str]:
        """Generate performance insights using Gemini"""
        try:
            insights_prompt = f"""
            Analyze these system performance trends and provide insights:
            
            {json.dumps(trends_data, indent=2)}
            
            Provide 3-5 actionable insights about:
            1. Current system health
            2. Performance trends
            3. Potential issues
            4. Optimization opportunities
            
            Format as a JSON array of insight strings.
            """
            
            response = await self.gemini_client.generate_content(
                prompt=insights_prompt,
                system_instruction="You are a performance analyst providing system optimization insights.",
                temperature=0.3,
                max_tokens=800
            )
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return ["Performance analysis completed"]
                
        except Exception as e:
            logger.error(f"Error generating performance insights: {e}")
            return ["Performance monitoring active"]
    
    async def alert_processing_loop(self):
        """Process incoming alert requests"""
        while self.running:
            try:
                # Check for alert requests from other agents
                messages = await self.get_messages("monitoring_alert")
                
                for message in messages:
                    await self.process_external_alert(message)
                
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in alert processing loop: {e}")
                await asyncio.sleep(30)
    
    async def process_external_alert(self, message: Dict[str, Any]):
        """Process alert from external source"""
        try:
            data = message.get('data', {})
            alert = {
                "type": data.get('type', 'external'),
                "severity": data.get('severity', 'info'),
                "message": data.get('message', 'External alert'),
                "source": data.get('source', 'unknown'),
                "timestamp": datetime.now().isoformat()
            }
            
            await self.process_alert(alert)
            
        except Exception as e:
            logger.error(f"Error processing external alert: {e}")
    
    async def store_metrics(self, metrics: SystemMetrics):
        """Store metrics in history and database"""
        try:
            # Add to in-memory history
            self.metrics_history.append(metrics)
            
            # Limit history size
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history = self.metrics_history[-self.max_history_size:]
            
            # Store in database (if available)
            await self.execute_query(
                "INSERT INTO system_metrics (cpu_usage, memory_usage, disk_usage, network_io, response_times, error_rates, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    metrics.cpu_usage,
                    metrics.memory_usage,
                    metrics.disk_usage,
                    json.dumps(metrics.network_io),
                    json.dumps(metrics.response_times),
                    json.dumps(metrics.error_rates),
                    metrics.timestamp
                ]
            )
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    async def store_health_checks(self, health_checks: List[HealthCheck]):
        """Store health check results"""
        try:
            for check in health_checks:
                await self.execute_query(
                    "INSERT INTO health_checks (service_name, status, response_time, error_message, timestamp) VALUES (?, ?, ?, ?, ?)",
                    [check.service_name, check.status, check.response_time, check.error_message, check.timestamp]
                )
        except Exception as e:
            logger.error(f"Error storing health checks: {e}")
    
    async def store_alert(self, alert: Dict[str, Any], diagnostics: Dict[str, Any]):
        """Store alert and diagnostics"""
        try:
            await self.execute_query(
                "INSERT INTO alerts (type, severity, message, diagnostics, timestamp) VALUES (?, ?, ?, ?, ?)",
                [alert["type"], alert["severity"], alert["message"], json.dumps(diagnostics), datetime.now()]
            )
        except Exception as e:
            logger.error(f"Error storing alert: {e}")
    
    async def store_performance_analysis(self, analysis: Dict[str, Any]):
        """Store performance analysis results"""
        try:
            await self.execute_query(
                "INSERT INTO performance_analysis (analysis_data, timestamp) VALUES (?, ?)",
                [json.dumps(analysis), datetime.now()]
            )
        except Exception as e:
            logger.error(f"Error storing performance analysis: {e}")
    
    async def handle_service_issue(self, health_check: HealthCheck):
        """Handle service health issues"""
        try:
            logger.warning(f"Service issue detected: {health_check.service_name} is {health_check.status}")
            
            # Generate service-specific diagnostics
            diagnostics = await self.diagnose_service_issue(health_check)
            
            # Attempt automated recovery
            if health_check.service_name in ["backend", "frontend"]:
                await self.attempt_service_restart(health_check.service_name)
            
        except Exception as e:
            logger.error(f"Error handling service issue: {e}")
    
    async def diagnose_service_issue(self, health_check: HealthCheck) -> Dict[str, Any]:
        """Diagnose service issues"""
        return {
            "service": health_check.service_name,
            "status": health_check.status,
            "response_time": health_check.response_time,
            "error": health_check.error_message,
            "recommendations": ["Check service logs", "Verify configuration", "Restart if necessary"]
        }
    
    async def attempt_service_restart(self, service_name: str):
        """Attempt to restart a service (placeholder)"""
        logger.info(f"Would attempt to restart service: {service_name}")
        # This would contain actual service restart logic
    
    async def attempt_resource_optimization(self, alert: Dict[str, Any]):
        """Attempt automated resource optimization"""
        logger.info(f"Would attempt resource optimization for: {alert['type']}")
        # This would contain actual optimization logic
    
    async def send_critical_alert_notification(self, alert: Dict[str, Any], diagnostics: Dict[str, Any]):
        """Send critical alert notifications"""
        logger.critical(f"CRITICAL ALERT: {alert['message']}")
        # This would send actual notifications (email, Slack, etc.)

# Agent factory function
def create_monitoring_agent() -> MonitoringAgent:
    """Create and return a Monitoring Agent instance"""
    return MonitoringAgent()
