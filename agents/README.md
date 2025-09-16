# Multi-Agent System

This directory contains the multi-agent system for EduLMS v2, featuring 7 specialized AI agents orchestrated by a Master Agent.

## Agent Structure

- `base/` - Base agent classes and shared utilities
- `specialized/` - Individual specialized agents
- `communication/` - TiDB-based communication services
- `workflows/` - Prefect workflow definitions
- `config/` - Agent configuration files
- `tests/` - Agent testing suite

## Agents

1. **Master Agent** - System orchestrator and workflow coordinator
2. **Content Curator Agent** - Educational content discovery and quality assessment
3. **Learning Path Agent** - Personalized learning journey design
4. **Assessment Agent** - Educational assessment creation and evaluation
5. **Tutor Agent** - Personalized instruction and adaptive explanations
6. **Research Agent** - Information gathering and synthesis
7. **Analytics Agent** - Learning data analysis and insight generation

## Communication

All agents communicate through TiDB database tables for reliable, queryable message passing and state management.