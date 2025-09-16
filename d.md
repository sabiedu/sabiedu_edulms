# SabiLearn: Redefining Education with AI

## Inspiration
At [Sabiedu](https://sabiedu.com), we’re passionate about making education *personalized* and *accessible* for all. The TiDB AgentX Hackathon 2025 inspired us to evolve **SabiLearn** into a next-generation AI-powered Learning Management System (LMS) that harnesses multi-agent orchestration to deliver truly adaptive learning experiences. Building on our v1 foundation, we replaced the monolithic Strapi backend with a sophisticated FastAPI implementation, integrated 9 specialized AI agents, and leveraged TiDB Serverless for advanced vector search and workflow automation. Our goal remains empowering students in underserved communities with intelligent, personalized education while equipping educators with powerful AI tools to automate and enhance their work.

## What it does
SabiLearn v2 delivers hyper-personalized education through a comprehensive multi-agent AI ecosystem:
- **Intelligent Content Discovery**: Semantic search across courses, lessons, and materials using TiDB vector embeddings for precise relevance.
- **Adaptive Learning Paths**: AI-generated study plans that dynamically adjust based on student performance, goals, and learning analytics.
- **Automated Assessment & Grading**: AI-powered quiz generation, real-time grading, and personalized feedback loops.
- **Multi-Step Workflows**: Orchestrated agent chains for content creation, research synthesis, and personalized tutoring.
- **Real-Time Analytics**: Comprehensive learning tracking with predictive insights and system monitoring.

It’s open-source, scalable, and designed for global impact, supporting institutions and individual learners with enterprise-grade features.

## How we built it
SabiLearn v2’s architecture is built for scalability and AI-first education:
- **Frontend**: [Nuxt.js](https://nuxt.com) with TypeScript and Vue.js for a responsive, accessible student portal and instructor dashboard with composables for seamless API integration.
- **Backend**: [FastAPI](https://fastapi.tiangolo.com) with async support, JWT authentication, and comprehensive REST APIs, replacing Strapi for superior performance and Python agent integration.
- **AI Workflows**: Custom multi-agent orchestrator coordinating 9 Python agents (Research, Analytics, Assessment, Tutor, Content Generation, Personalization, Content Curator, Learning Path, Monitoring) using Google Gemini for LLM calls and external tool invocations.
- **Database**: [TiDB Serverless](https://www.pingcap.com/tidb-serverless) with vector search capabilities storing relational data and 768-dimensional embeddings, enabling queries like:
  ```sql
  SELECT content_id, title, VEC_COSINE_DISTANCE(embedding, ?) as similarity
  FROM content_embeddings
  WHERE content_type IN ('course', 'lesson', 'assessment')
  ORDER BY similarity ASC
  LIMIT 20;
  ```
- **External Services**: Google Gemini API for AI processing, integrated with async workflows for chaining LLM calls and tool invocations.

The agentic system ingests educational content, performs vector similarity searches using \( \text{VEC_COSINE_DISTANCE}(\vec{a}, \vec{b}) \), orchestrates multi-step workflows (e.g., research-to-content generation), and delivers personalized learning experiences through automated agent collaboration.

## Challenges we ran into
Migrating from OpenAI to Google Gemini across all agents required extensive API refactoring and fallback mechanisms for reliability. Ensuring seamless integration between the FastAPI backend, Nuxt.js frontend, and TiDB vector operations demanded careful handling of async database connections and CORS configurations. Debugging multi-agent workflow dependencies and optimizing vector search performance for real-time responses tested our database engineering skills. Building an accessible, WCAG-compliant UI while managing the complexity of 9 interacting agents under the hackathon’s deadline (Sep 16, 2025) pushed our development and testing capabilities.

## Accomplishments that we're proud of
- Developed a production-ready, open-source LMS v2 with an MIT license, featuring a complete multi-agent orchestration system and hosted on [GitHub](https://github.com/yourusername/sabilearn-v2).
- Achieved full hackathon compliance: data ingestion/indexing, vector search, LLM call chaining, external tool invocations, and multi-step workflow automation using TiDB Serverless.
- Delivered a fully integrated system with 9 AI agents, 5 predefined workflows, and end-to-end functionality from content creation to personalized learning delivery.
- Positioned SabiLearn v2 to compete for $16,000 in hackathon prizes, including Social Good and Best Open Source Awards, with demonstrated real-world educational impact.

## What we learned
We deepened our expertise in **TiDB Serverless** vector operations, mastering cosine distance calculations \( \text{VEC_COSINE_DISTANCE}(\vec{a}, \vec{b}) = 1 - \frac{\vec{a} \cdot \vec{b}}{||\vec{a}|| \cdot ||\vec{b}||} \) for semantic search. FastAPI and async Python taught us to build high-performance APIs, while multi-agent orchestration revealed the power of coordinated AI workflows. We refined our skills in accessibility-first design and gained valuable insights into scalable EdTech architectures that balance AI complexity with user experience.

## What's next for SabiLearn
Post-hackathon, we’ll expand SabiLearn v2 into a market-leading platform:
- Integrate with educational ecosystems like Google Classroom, Canvas, and Zoom for broader workflow automation.
- Launch a freemium model with premium features for advanced analytics, multilingual support, and institutional licensing.
- Develop a course marketplace and content creator tools to monetize while supporting open education.
- Foster community growth through enhanced open-source contributions and partnerships with educational institutions.

SabiLearn v2 will continue driving Sabiedu’s mission to democratize education globally, building on a strong hackathon foundation to create lasting impact!

![SabiLearn v2 Screenshot](/path/to/sabilearn-v2-screenshot.jpg)
