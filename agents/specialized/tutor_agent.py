"""
Tutor Agent Worker

A minimal worker that polls TiDB-backed message queues via TiDBCommunicationService
and responds to messages on a demo channel. Uses an LLM if configured, otherwise
falls back to a simple rule-based response.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional, Dict, Any, List

from agents.communication.tidb_service import TiDBCommunicationService, AgentMessage
from agents.communication.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)


class TutorAgentWorker:
    def __init__(
        self,
        comms: TiDBCommunicationService,
        channel: str = "demo",
        agent_name: str = "tutor-agent",
        recipient_agent: str = "frontend",
        polling_interval: float = 1.0,
    ) -> None:
        self.comms = comms
        self.channel = channel
        self.agent_name = agent_name
        self.recipient_agent = recipient_agent
        self.polling_interval = polling_interval
        self._stopping = asyncio.Event()

        # LLM config (optional)
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.gemini_model = os.getenv("GOOGLE_GEMINI_MODEL", "gemini-2.0-flash-001")

        # Lazy client init
        self._gemini_client = None

    async def run(self) -> None:
        logger.info(
            "TutorAgentWorker starting: channel=%s agent=%s recipient=%s",
            self.channel,
            self.agent_name,
            self.recipient_agent,
        )

        while not self._stopping.is_set():
            try:
                messages = await self.comms.poll_messages(
                    channel=self.channel,
                    agent_name=self.agent_name,
                    limit=10,
                    include_processed=False,
                )

                if messages:
                    await self._process_batch(messages)

            except Exception as e:
                logger.error("TutorAgentWorker loop error: %s", e)

            # Sleep between polls
            try:
                await asyncio.wait_for(self._stopping.wait(), timeout=self.polling_interval)
            except asyncio.TimeoutError:
                pass

        logger.info("TutorAgentWorker stopped")

    async def stop(self) -> None:
        self._stopping.set()

    async def _process_batch(self, messages: List[AgentMessage]) -> None:
        for msg in messages:
            try:
                await self._process_message(msg)
            except Exception as e:
                logger.exception("Failed processing message id=%s: %s", msg.id, e)

    async def _process_message(self, msg: AgentMessage) -> None:
        payload = msg.message or {}
        user_text = self._extract_user_text(payload)
        logger.info(
            "Processing message id=%s from=%s -> %s: %s",
            msg.id,
            msg.sender_agent,
            self.agent_name,
            user_text,
        )

        reply_text = await self._generate_reply(user_text, payload)

        # Send reply back to the frontend listener
        await self.comms.send_message(
            channel=self.channel,
            sender_agent=self.agent_name,
            message={
                "type": "agent_reply",
                "text": reply_text,
                "in_reply_to": msg.id,
            },
            recipient_agent=self.recipient_agent,
            priority=5,
        )

        # Mark original as processed
        if msg.id is not None:
            await self.comms.mark_message_processed(message_id=msg.id, processed_by=self.agent_name)
            logger.info("Marked message id=%s as processed", msg.id)

    def _extract_user_text(self, payload: Dict[str, Any]) -> str:
        # Common shapes: { text }, { message: { text } } etc.
        if isinstance(payload, dict):
            if "text" in payload and isinstance(payload["text"], str):
                return payload["text"].strip()
            inner = payload.get("message")
            if isinstance(inner, dict) and isinstance(inner.get("text"), str):
                return inner["text"].strip()
        return ""

    async def _generate_reply(self, user_text: str, payload: Dict[str, Any]) -> str:
        # Prefer LLM if available
        if self.google_api_key:
            try:
                if self._gemini_client is None:
                    self._gemini_client = get_gemini_client()

                messages = [
                    {"role": "user", "content": user_text}
                ]

                system_instruction = (
                    "You are a concise tutor agent for an LMS. Provide a short, helpful reply "
                    "in under 2 sentences. If the question is unclear, ask a clarifying question."
                )

                content = await self._gemini_client.chat_completion(
                    messages=messages,
                    system_instruction=system_instruction,
                    temperature=0.5,
                    max_tokens=120
                )
                
                if content:
                    return content.strip()
            except Exception as e:
                logger.warning("LLM generation failed, falling back to rule-based: %s", e)

        # Fallback: simple rule-based echo with light guidance
        if not user_text:
            return "Hi! I’m your Tutor Agent. Ask me a question about your course or lesson."
        if any(k in user_text.lower() for k in ["help", "how do", "what is", "explain"]):
            return (
                "Here’s a quick tip: try breaking the problem into smaller steps. "
                "What have you tried so far?"
            )
        return f"You said: '{user_text}'. Could you share your goal so I can assist better?"
