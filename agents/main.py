import asyncio
import logging
import os
from typing import Dict, Any

from .communication.tidb_service import TiDBCommunicationService
from .specialized.tutor_agent import TutorAgentWorker
from .specialized.assessment_agent import run_assessment_agent
from .specialized.learning_path_agent import run_learning_path_agent
from .specialized.content_curator_agent import run_content_curator_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentSystemManager:
    def __init__(self):
        self.comm_service = TiDBCommunicationService()
        self.agents = {}
        self.running = False
        
    async def start_agents(self):
        """Start all configured agents"""
        logger.info("Starting Agent System Manager...")
        
        # Initialize communication service
        await self.comm_service.initialize()
        
        # Start agents based on environment configuration
        if os.getenv('ENABLE_TUTOR_AGENT', 'true').lower() == 'true':
            logger.info("Starting Tutor Agent...")
            tutor_worker = TutorAgentWorker()
            self.agents['tutor'] = asyncio.create_task(tutor_worker.start())
            
        if os.getenv('ENABLE_ASSESSMENT_AGENT', 'true').lower() == 'true':
            logger.info("Starting Assessment Agent...")
            self.agents['assessment'] = asyncio.create_task(run_assessment_agent())
            
        if os.getenv('ENABLE_LEARNING_PATH_AGENT', 'true').lower() == 'true':
            logger.info("Starting Learning Path Agent...")
            self.agents['learning_path'] = asyncio.create_task(run_learning_path_agent())
            
        if os.getenv('ENABLE_CONTENT_CURATOR_AGENT', 'true').lower() == 'true':
            logger.info("Starting Content Curator Agent...")
            self.agents['content_curator'] = asyncio.create_task(run_content_curator_agent())
            
        self.running = True
        logger.info(f"Started {len(self.agents)} agents")
        
    async def stop_agents(self):
        """Stop all running agents"""
        logger.info("Stopping agents...")
        self.running = False
        
        for agent_name, task in self.agents.items():
            logger.info(f"Stopping {agent_name} agent...")
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
        self.agents.clear()
        logger.info("All agents stopped")
        
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all agents"""
        health_status = {
            'system_running': self.running,
            'agents': {},
            'communication': await self.comm_service.health_check()
        }
        
        for agent_name, task in self.agents.items():
            health_status['agents'][agent_name] = {
                'running': not task.done(),
                'cancelled': task.cancelled(),
                'exception': str(task.exception()) if task.done() and task.exception() else None
            }
            
        return health_status
        
    async def run_forever(self):
        """Run the agent system indefinitely"""
        try:
            await self.start_agents()
            
            # Keep running until interrupted
            while self.running:
                await asyncio.sleep(10)
                
                # Check agent health
                health = await self.health_check()
                if not all(agent['running'] for agent in health['agents'].values()):
                    logger.warning("Some agents are not running properly")
                    
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Agent system error: {e}")
        finally:
            await self.stop_agents()

async def main():
    """Main entry point for the agent system"""
    manager = AgentSystemManager()
    await manager.run_forever()

if __name__ == "__main__":
    asyncio.run(main())