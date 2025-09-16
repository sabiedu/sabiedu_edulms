"""
Trigger Notification and Polling Services for Agent Communication

This module provides real-time notification services and efficient polling
mechanisms for agent communication using database triggers and subscriptions.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Set
from dataclasses import dataclass
from enum import Enum
import threading
import time

from .tidb_service import TiDBCommunicationService, AgentMessage

logger = logging.getLogger(__name__)


class SubscriptionType(Enum):
    """Subscription type enumeration."""
    ALL = "all"
    DIRECT = "direct"
    PATTERN = "pattern"


@dataclass
class Subscription:
    """Agent subscription data structure."""
    agent_name: str
    channel: str
    subscription_type: SubscriptionType
    pattern: Optional[str] = None
    callback: Optional[Callable] = None
    last_poll: Optional[datetime] = None
    message_count: int = 0


@dataclass
class NotificationEvent:
    """Notification event data structure."""
    event_type: str
    channel: str
    data: Dict[str, Any]
    timestamp: datetime
    source_agent: Optional[str] = None


class TriggerNotificationService:
    """
    Real-time notification service for agent communication.
    
    Provides database trigger-based notifications and subscription management
    for efficient agent coordination and real-time updates.
    """

    def __init__(self, communication_service: TiDBCommunicationService):
        """
        Initialize trigger notification service.
        
        Args:
            communication_service: TiDB communication service instance
        """
        self.comm_service = communication_service
        self.subscriptions: Dict[str, List[Subscription]] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.running = False
        self.notification_tasks: List[asyncio.Task] = []

    async def subscribe_agent(
        self,
        agent_name: str,
        channel: str,
        subscription_type: SubscriptionType = SubscriptionType.ALL,
        pattern: Optional[str] = None,
        callback: Optional[Callable] = None
    ) -> None:
        """
        Subscribe an agent to a channel for notifications.
        
        Args:
            agent_name: Agent name
            channel: Channel to subscribe to
            subscription_type: Type of subscription
            pattern: Pattern for pattern-based subscriptions
            callback: Optional callback function for notifications
        """
        # Store subscription in database
        insert_query = """
        INSERT INTO agent_subscriptions (agent_name, channel, subscription_type, pattern)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        subscription_type = VALUES(subscription_type),
        pattern = VALUES(pattern)
        """
        
        try:
            await self.comm_service._execute_query(
                insert_query,
                (agent_name, channel, subscription_type.value, pattern)
            )
            
            # Store in memory for quick access
            if channel not in self.subscriptions:
                self.subscriptions[channel] = []
            
            # Remove existing subscription for this agent/channel
            self.subscriptions[channel] = [
                sub for sub in self.subscriptions[channel] 
                if sub.agent_name != agent_name
            ]
            
            # Add new subscription
            subscription = Subscription(
                agent_name=agent_name,
                channel=channel,
                subscription_type=subscription_type,
                pattern=pattern,
                callback=callback,
                last_poll=datetime.now()
            )
            
            self.subscriptions[channel].append(subscription)
            
            logger.info(f"Agent {agent_name} subscribed to channel {channel} ({subscription_type.value})")
            
        except Exception as e:
            logger.error(f"Failed to subscribe agent {agent_name} to channel {channel}: {e}")
            raise

    async def unsubscribe_agent(self, agent_name: str, channel: str) -> None:
        """
        Unsubscribe an agent from a channel.
        
        Args:
            agent_name: Agent name
            channel: Channel to unsubscribe from
        """
        # Remove from database
        delete_query = """
        DELETE FROM agent_subscriptions 
        WHERE agent_name = %s AND channel = %s
        """
        
        try:
            await self.comm_service._execute_query(delete_query, (agent_name, channel))
            
            # Remove from memory
            if channel in self.subscriptions:
                self.subscriptions[channel] = [
                    sub for sub in self.subscriptions[channel] 
                    if sub.agent_name != agent_name
                ]
                
                if not self.subscriptions[channel]:
                    del self.subscriptions[channel]
            
            logger.info(f"Agent {agent_name} unsubscribed from channel {channel}")
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe agent {agent_name} from channel {channel}: {e}")
            raise

    async def get_agent_subscriptions(self, agent_name: str) -> List[Subscription]:
        """
        Get all subscriptions for an agent.
        
        Args:
            agent_name: Agent name
            
        Returns:
            List of agent subscriptions
        """
        query = """
        SELECT channel, subscription_type, pattern FROM agent_subscriptions
        WHERE agent_name = %s
        """
        
        try:
            results = await self.comm_service._execute_query(query, (agent_name,), fetch=True)
            
            subscriptions = []
            if results:
                for row in results:
                    subscription = Subscription(
                        agent_name=agent_name,
                        channel=row["channel"],
                        subscription_type=SubscriptionType(row["subscription_type"]),
                        pattern=row["pattern"]
                    )
                    subscriptions.append(subscription)
            
            return subscriptions
            
        except Exception as e:
            logger.error(f"Failed to get subscriptions for agent {agent_name}: {e}")
            return []

    async def notify_subscribers(
        self,
        channel: str,
        event_type: str,
        data: Dict[str, Any],
        source_agent: Optional[str] = None
    ) -> int:
        """
        Notify all subscribers of a channel event.
        
        Args:
            channel: Channel name
            event_type: Type of event
            data: Event data
            source_agent: Agent that triggered the event
            
        Returns:
            Number of agents notified
        """
        if channel not in self.subscriptions:
            return 0
        
        event = NotificationEvent(
            event_type=event_type,
            channel=channel,
            data=data,
            timestamp=datetime.now(),
            source_agent=source_agent
        )
        
        notified_count = 0
        
        for subscription in self.subscriptions[channel]:
            try:
                # Check subscription type and filters
                should_notify = False
                
                if subscription.subscription_type == SubscriptionType.ALL:
                    should_notify = True
                elif subscription.subscription_type == SubscriptionType.DIRECT:
                    # Only notify if message is directly addressed to this agent
                    should_notify = data.get("recipient_agent") == subscription.agent_name
                elif subscription.subscription_type == SubscriptionType.PATTERN:
                    # Check if event matches pattern
                    if subscription.pattern:
                        should_notify = subscription.pattern in str(data)
                
                if should_notify:
                    # Call callback if provided
                    if subscription.callback:
                        try:
                            if asyncio.iscoroutinefunction(subscription.callback):
                                await subscription.callback(event)
                            else:
                                subscription.callback(event)
                        except Exception as e:
                            logger.error(f"Callback error for {subscription.agent_name}: {e}")
                    
                    # Update subscription stats
                    subscription.message_count += 1
                    notified_count += 1
            
            except Exception as e:
                logger.error(f"Failed to notify {subscription.agent_name}: {e}")
        
        logger.debug(f"Notified {notified_count} subscribers for channel {channel}")
        return notified_count

    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for {event_type}")

    async def trigger_event(
        self,
        event_type: str,
        channel: str,
        data: Dict[str, Any],
        source_agent: Optional[str] = None
    ) -> None:
        """
        Trigger an event and notify subscribers.
        
        Args:
            event_type: Type of event
            channel: Channel name
            data: Event data
            source_agent: Agent that triggered the event
        """
        # Execute registered event handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(channel, data, source_agent)
                    else:
                        handler(channel, data, source_agent)
                except Exception as e:
                    logger.error(f"Event handler error for {event_type}: {e}")
        
        # Notify subscribers
        await self.notify_subscribers(channel, event_type, data, source_agent)

    async def start_notification_service(self) -> None:
        """Start the notification service background tasks."""
        if self.running:
            return
        
        self.running = True
        
        # Load existing subscriptions from database
        await self._load_subscriptions()
        
        logger.info("Trigger notification service started")

    async def stop_notification_service(self) -> None:
        """Stop the notification service."""
        self.running = False
        
        # Cancel all notification tasks
        for task in self.notification_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.notification_tasks.clear()
        logger.info("Trigger notification service stopped")

    async def _load_subscriptions(self) -> None:
        """Load existing subscriptions from database."""
        query = """
        SELECT agent_name, channel, subscription_type, pattern 
        FROM agent_subscriptions
        """
        
        try:
            results = await self.comm_service._execute_query(query, fetch=True)
            
            if results:
                for row in results:
                    channel = row["channel"]
                    if channel not in self.subscriptions:
                        self.subscriptions[channel] = []
                    
                    subscription = Subscription(
                        agent_name=row["agent_name"],
                        channel=channel,
                        subscription_type=SubscriptionType(row["subscription_type"]),
                        pattern=row["pattern"],
                        last_poll=datetime.now()
                    )
                    
                    self.subscriptions[channel].append(subscription)
            
            logger.info(f"Loaded {len(results) if results else 0} subscriptions from database")
            
        except Exception as e:
            logger.error(f"Failed to load subscriptions: {e}")


class MessagePollingService:
    """
    Efficient message polling service for agent communication.
    
    Provides optimized polling mechanisms with backoff strategies,
    batch processing, and subscription-based filtering.
    """

    def __init__(self, communication_service: TiDBCommunicationService):
        """
        Initialize message polling service.
        
        Args:
            communication_service: TiDB communication service instance
        """
        self.comm_service = communication_service
        self.polling_agents: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.polling_tasks: List[asyncio.Task] = []
        self.default_poll_interval = 5  # seconds
        self.max_poll_interval = 60  # seconds
        self.backoff_multiplier = 1.5

    async def start_polling_for_agent(
        self,
        agent_name: str,
        channels: List[str],
        callback: Callable[[List[AgentMessage]], None],
        poll_interval: int = 5,
        batch_size: int = 10
    ) -> None:
        """
        Start polling for messages for a specific agent.
        
        Args:
            agent_name: Agent name
            channels: List of channels to poll
            callback: Callback function for received messages
            poll_interval: Polling interval in seconds
            batch_size: Maximum messages per poll
        """
        if agent_name in self.polling_agents:
            await self.stop_polling_for_agent(agent_name)
        
        self.polling_agents[agent_name] = {
            "channels": channels,
            "callback": callback,
            "poll_interval": poll_interval,
            "batch_size": batch_size,
            "current_interval": poll_interval,
            "last_poll": datetime.now(),
            "message_count": 0,
            "error_count": 0
        }
        
        # Start polling task
        task = asyncio.create_task(self._poll_agent_messages(agent_name))
        self.polling_tasks.append(task)
        
        logger.info(f"Started polling for agent {agent_name} on channels {channels}")

    async def stop_polling_for_agent(self, agent_name: str) -> None:
        """
        Stop polling for a specific agent.
        
        Args:
            agent_name: Agent name
        """
        if agent_name in self.polling_agents:
            del self.polling_agents[agent_name]
        
        # Cancel agent's polling task
        tasks_to_remove = []
        for task in self.polling_tasks:
            if not task.done() and hasattr(task, '_agent_name') and task._agent_name == agent_name:
                task.cancel()
                tasks_to_remove.append(task)
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        for task in tasks_to_remove:
            self.polling_tasks.remove(task)
        
        logger.info(f"Stopped polling for agent {agent_name}")

    async def _poll_agent_messages(self, agent_name: str) -> None:
        """
        Background polling task for an agent.
        
        Args:
            agent_name: Agent name
        """
        # Store agent name in task for identification
        current_task = asyncio.current_task()
        if current_task:
            current_task._agent_name = agent_name
        
        while self.running and agent_name in self.polling_agents:
            try:
                agent_config = self.polling_agents[agent_name]
                
                # Poll messages from all subscribed channels
                all_messages = []
                
                for channel in agent_config["channels"]:
                    try:
                        messages = await self.comm_service.poll_messages(
                            channel=channel,
                            agent_name=agent_name,
                            limit=agent_config["batch_size"]
                        )
                        all_messages.extend(messages)
                        
                    except Exception as e:
                        logger.error(f"Failed to poll channel {channel} for {agent_name}: {e}")
                        agent_config["error_count"] += 1
                
                # Process messages if any
                if all_messages:
                    try:
                        # Call callback with messages
                        callback = agent_config["callback"]
                        if asyncio.iscoroutinefunction(callback):
                            await callback(all_messages)
                        else:
                            callback(all_messages)
                        
                        # Mark messages as processed
                        for message in all_messages:
                            if message.id:
                                await self.comm_service.mark_message_processed(
                                    message.id, agent_name
                                )
                        
                        # Update stats
                        agent_config["message_count"] += len(all_messages)
                        agent_config["last_poll"] = datetime.now()
                        
                        # Reset polling interval on successful processing
                        agent_config["current_interval"] = agent_config["poll_interval"]
                        
                        logger.debug(f"Processed {len(all_messages)} messages for {agent_name}")
                        
                    except Exception as e:
                        logger.error(f"Message processing error for {agent_name}: {e}")
                        agent_config["error_count"] += 1
                
                else:
                    # No messages, apply backoff
                    current_interval = agent_config["current_interval"]
                    new_interval = min(
                        current_interval * self.backoff_multiplier,
                        self.max_poll_interval
                    )
                    agent_config["current_interval"] = new_interval
                
                # Wait for next poll
                await asyncio.sleep(agent_config["current_interval"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Polling error for {agent_name}: {e}")
                agent_config["error_count"] += 1
                await asyncio.sleep(agent_config["poll_interval"])

    async def get_polling_stats(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get polling statistics.
        
        Args:
            agent_name: Optional agent filter
            
        Returns:
            Polling statistics
        """
        if agent_name:
            if agent_name in self.polling_agents:
                config = self.polling_agents[agent_name]
                return {
                    "agent_name": agent_name,
                    "channels": config["channels"],
                    "poll_interval": config["poll_interval"],
                    "current_interval": config["current_interval"],
                    "last_poll": config["last_poll"].isoformat() if config["last_poll"] else None,
                    "message_count": config["message_count"],
                    "error_count": config["error_count"],
                    "success_rate": (config["message_count"] / (config["message_count"] + config["error_count"])) if (config["message_count"] + config["error_count"]) > 0 else 1.0
                }
            else:
                return {"error": f"Agent {agent_name} not found"}
        
        # Return stats for all agents
        stats = {}
        for name, config in self.polling_agents.items():
            stats[name] = {
                "channels": config["channels"],
                "poll_interval": config["poll_interval"],
                "current_interval": config["current_interval"],
                "last_poll": config["last_poll"].isoformat() if config["last_poll"] else None,
                "message_count": config["message_count"],
                "error_count": config["error_count"],
                "success_rate": (config["message_count"] / (config["message_count"] + config["error_count"])) if (config["message_count"] + config["error_count"]) > 0 else 1.0
            }
        
        return {
            "total_agents": len(self.polling_agents),
            "running": self.running,
            "agents": stats
        }

    async def start_polling_service(self) -> None:
        """Start the polling service."""
        if self.running:
            return
        
        self.running = True
        logger.info("Message polling service started")

    async def stop_polling_service(self) -> None:
        """Stop the polling service."""
        self.running = False
        
        # Stop all agent polling
        agent_names = list(self.polling_agents.keys())
        for agent_name in agent_names:
            await self.stop_polling_for_agent(agent_name)
        
        logger.info("Message polling service stopped")

    async def update_agent_channels(self, agent_name: str, channels: List[str]) -> None:
        """
        Update channels for an agent.
        
        Args:
            agent_name: Agent name
            channels: New list of channels
        """
        if agent_name in self.polling_agents:
            self.polling_agents[agent_name]["channels"] = channels
            logger.info(f"Updated channels for {agent_name}: {channels}")

    async def get_unprocessed_count(self, agent_name: str, channel: str) -> int:
        """
        Get count of unprocessed messages for an agent in a channel.
        
        Args:
            agent_name: Agent name
            channel: Channel name
            
        Returns:
            Number of unprocessed messages
        """
        return await self.comm_service.get_unprocessed_message_count(channel, agent_name)