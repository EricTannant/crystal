# Crystal - Personal Assistant AI Project

## Project Vision

A suite of personal AI assistants with gemstone-themed names designed to help with various daily tasks and system management.

## Core Concept

- **Primary Assistant**: Ruby (main general-purpose assistant)
- **Naming Convention**: All assistants named after gemstones (Ruby, Emerald, Diamond, etc.)
- **Specialization**: Different assistants can be specialized for different types of tasks

## Planned Capabilities

### General Tasks (Ruby - Main Assistant)

- **Schedule Management**
  - Calendar integration
  - Appointment scheduling
  - Reminder system
  - Meeting coordination

- **File Organization**
  - Automated file sorting
  - Duplicate detection and cleanup
  - Folder structure optimization
  - File search and retrieval

- **System Job Management**
  - Running background tasks
  - System monitoring
  - Automated maintenance scripts
  - Process management

- **Extensible Framework**
  - Plugin system for additional capabilities
  - Easy addition of new specialized assistants
  - Cross-assistant communication

### Potential Specialized Assistants

- **Emerald**: Development/coding tasks
- **Diamond**: Data analysis and reporting
- **Sapphire**: Communication and email management
- **Opal**: Creative tasks (writing, design assistance)
- **Topaz**: Financial management and tracking
- **Garnet**: Health and wellness tracking

## Technical Architecture (To Be Determined)

### Architecture Overview

**Local PC Application with Web Interface**

- Backend server runs locally on your PC
- Web-based frontend accessible via browser (localhost)
- Mobile access through responsive design or PWA
- All data stays local for privacy and speed

### Core Components

- [ ] Main orchestration engine
- [ ] Natural language processing (Python AI libraries)
- [ ] Task scheduling system (APScheduler or Celery)
- [ ] File system integration (pathlib, watchdog)
- [ ] **FastAPI web server** (with automatic API docs)
- [ ] **CLI interface** (Click or Typer for command-line access)
- [ ] **WebSocket support** (for real-time chat with Ruby)
- [ ] **PostgreSQL integration** (SQLAlchemy ORM)
- [ ] Configuration management (Pydantic settings)
- [ ] Logging and monitoring (Python logging + structured logs)
- [ ] **Authentication system** (FastAPI security utilities)

### Integration Points

- [ ] Calendar systems (Google Calendar, Outlook, etc.)
- [ ] File systems (local, cloud storage)
- [ ] Operating system APIs
- [ ] Third-party services APIs
- [ ] Communication platforms

## Development Phases

### Phase 1: Foundation

- [ ] Project structure setup
- [ ] Core framework design
- [ ] **Local web server setup** (choose port, basic routing)
- [ ] **Basic web interface** (HTML/CSS/JS foundation)
- [ ] Basic Ruby assistant implementation
- [ ] Simple task execution system

### Phase 2: Core Features

- [ ] Schedule management implementation
- [ ] File organization system
- [ ] System job management
- [ ] Configuration system

### Phase 3: Expansion

- [ ] Additional specialized assistants
- [ ] Advanced integrations
- [ ] **Mobile responsiveness** (responsive design or PWA)
- [ ] **Mobile app features** (offline capabilities, push notifications)
- [ ] User interface improvements
- [ ] Plugin system

### Phase 4: Polish

- [ ] Performance optimization
- [ ] Error handling and recovery
- [ ] Documentation and tutorials
- [ ] Security hardening

## Technology Stack Considerations

- **Programming Language**: **Python** (excellent for AI/ML integration and rapid development)
- **Web Framework**: **FastAPI** (modern, fast, auto-generated API docs, WebSocket support)
- **AI/ML Framework**: TBD (OpenAI API, local models via Hugging Face/Ollama?)
- **Database**: **PostgreSQL** (robust, supports JSON, excellent for complex queries)
- **UI Framework**: Web-based (React, Vue.js, or vanilla HTML/CSS/JS)
- **CLI Framework**: **Typer** (modern, easy-to-use CLI with auto-completion)
- **Deployment**: Local PC application with web server
- **Mobile Access**: Progressive Web App (PWA) or responsive web design

### AI Model Recommendations for RTX 2060 Super (8GB VRAM)

**Hybrid Approach Recommended:**

- **Primary**: OpenAI API (GPT-4/GPT-3.5) for complex reasoning
- **Local Backup**: Smaller local models for basic tasks and privacy

**Best Local Models for Your Hardware:**

1. **Llama 3.1 8B** (via Ollama) - Excellent general purpose, fits in 8GB VRAM
2. **Qwen2.5 7B** - Great for coding tasks (Emerald assistant)
3. **Phi-3.5 Mini** (3.8B) - Microsoft's efficient model, very fast
4. **Code Llama 7B** - Specifically fine-tuned for programming tasks

**Memory Management Strategy:**

- Load models on-demand (swap based on assistant type)
- Use **Ollama** for easy model management and GPU memory optimization
- Implement model quantization (4-bit) to reduce VRAM usage
- Fall back to OpenAI API for complex tasks that need more capability

**Why This Hybrid Approach:**

- **Cost Effective**: Use local models for routine tasks, API for complex ones
- **Privacy**: Sensitive data can use local models
- **Reliability**: Always have OpenAI as backup if local model struggles
- **Performance**: Local models are instant, no API latency

### Why Python is Perfect for This Project

- **AI/ML Ecosystem**: Unmatched library support (OpenAI, Hugging Face, LangChain, etc.)
- **System Integration**: Excellent OS interaction capabilities (file management, process control)
- **Rapid Development**: Quick prototyping and iteration
- **Rich Libraries**: Schedule management (calendar), file operations, web scraping, etc.
- **FastAPI Benefits**: Automatic API documentation, type hints, async support, WebSocket for real-time chat

## Security & Privacy Considerations

- Local data processing preferences
- API key management
- User consent for system access
- Data encryption and storage
- Audit logging

## User Experience Goals

- Natural language interaction
- Minimal setup and configuration
- Reliable and predictable behavior
- Easy customization and extension
- Clear feedback and status reporting

## Questions to Resolve

1. What level of system access should the assistants have?
2. Which integrations are highest priority?
3. Should this use commercial AI APIs or local models?
4. **NEW**: What port should the local web server run on? (suggested: 8000)
5. **NEW**: Should mobile access be via PWA or responsive design?

## Next Steps

1. Define technical architecture
2. Choose technology stack
3. Create project structure
4. Implement basic Ruby assistant
5. Define task execution framework

---

*Last Updated: August 3, 2025*
*Repository: crystal (main branch)*
