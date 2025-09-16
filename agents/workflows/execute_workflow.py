#!/usr/bin/env python3
"""
Workflow Execution Script
Command-line interface for executing multi-agent workflows
"""

import asyncio
import argparse
import json
import sys
import os
from pathlib import Path

# Add agents directory to Python path
agents_dir = Path(__file__).parent.parent
sys.path.insert(0, str(agents_dir))

from workflows.multi_agent_orchestrator import MultiAgentOrchestrator

async def main():
    parser = argparse.ArgumentParser(description='Execute multi-agent workflows')
    parser.add_argument('--workflow', required=True, help='Workflow name to execute')
    parser.add_argument('--data', required=True, help='Initial data as JSON string')
    parser.add_argument('--user-id', help='User ID for the workflow')
    
    args = parser.parse_args()
    
    try:
        # Parse initial data
        initial_data = json.loads(args.data)
        
        if args.user_id:
            initial_data['user_id'] = args.user_id
        
        # Create orchestrator and execute workflow
        orchestrator = MultiAgentOrchestrator()
        result = await orchestrator.execute_workflow(args.workflow, initial_data)
        
        # Output result as JSON
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e),
            'workflow_name': args.workflow
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
