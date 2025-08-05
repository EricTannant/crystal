# Crystal - Personal Assistant AI Project

Your personal AI assistants, designed to help with daily tasks and system management.

## Features

- **Ruby**: Your main personal assistant for schedule management, file organization, system tasks, and general assistance
- **Multiple Interfaces**: Both web-based GUI and CLI access
- **Local + Cloud AI**: Hybrid approach using local models (Ollama) and OpenAI API
- **Privacy-First**: All data stays on your local PC
- **Modular Architecture**: Easy to extend with additional specialized assistants in the future

## Quick Start

### 1. Setup Python Virtual Environment

```powershell
# Create a virtual environment
python -m venv crystal-env

# Activate the virtual environment
crystal-env\Scripts\Activate.ps1

# If you get execution policy errors, run this first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify you're in the virtual environment (should show (crystal-env) in prompt)
```

### 2. Install Dependencies (Step-by-Step Method)

```powershell
# Upgrade pip first
python -m pip install --upgrade pip
```

Next install all the requirements.

```powershell
    pip install -r requirements.txt
```

### 3. Setup Database (PostgreSQL)

```powershell
# Step 1: Create the Crystal database and user
# Open PostgreSQL command line (psql) as postgres user
# You can find "SQL Shell (psql)" in your Start menu after PostgreSQL installation

# In psql, run these commands:
CREATE DATABASE crystal;
CREATE USER crystal WITH PASSWORD 'crystal';
GRANT ALL PRIVILEGES ON DATABASE crystal TO crystal;
\q

# Step 2: Test the connection
# Try connecting with the crystal user
psql -U crystal -d crystal -h localhost

# If successful, you should see: crystal=>
# Type \q to exit

# Step 3: Update your .env file
# Make sure your .env file has the correct DATABASE_URL:
# DATABASE_URL=postgresql://crystal:crystal@localhost/crystal

# Alternative: Use Docker (if you have Docker Desktop)
docker run --name crystal-postgres -e POSTGRES_DB=crystal -e POSTGRES_USER=crystal -e POSTGRES_PASSWORD=crystal -p 5432:5432 -d postgres:15
```

### 4. Configure AI Models

```powershell
# Option A: For OpenAI API copy the .env.sample file into .env and add your OPENAI API KEY
$env:OPENAI_API_KEY = "your-api-key-here"

# Option B: For local models (requires more setup but free)
# Install Ollama from: https://ollama.com/download
ollama pull llama3.1:8b
ollama pull phi3.5:mini
```

### 5. Start Ruby Assistant

```powershell
# Start the web server
python -m crystal.main

# Server will start at http://localhost:8000
```

### 6. Meet Ruby!

- **Web Interface**: Open http://localhost:8000 in your browser
- **API Documentation**: Visit http://localhost:8000/docs to explore the API
- **CLI Interface**: Open a new terminal and run `python -m crystal.cli --help`

### First Conversation with Ruby

Try asking Ruby:

- "Hello Ruby, what can you help me with?"
- "Can you help me organize my files?"
- "What's your status and capabilities?"
- "Can you help me schedule a reminder?"

## Project Structure

```bash
crystal/
├── crystal/                    # Main application package
│   ├── core/                  # Core system components
│   ├── assistants/            # Gemstone assistants (Ruby, Emerald, etc.)
│   ├── api/                   # FastAPI routes and WebSocket handlers
│   ├── cli/                   # Command-line interface
│   ├── models/                # Database models
│   ├── services/              # Business logic services
│   ├── utils/                 # Utility functions
│   └── web/                   # Web interface static files
├── config/                    # Configuration files
├── tests/                     # Test suite
├── migrations/                # Database migrations
└── docs/                      # Documentation
```

## Usage Examples

### Web Interface

- Navigate to <http://localhost:8000>
- Chat with Ruby in real-time via the web interface
- Ruby can help you organize files, manage schedules, and handle system tasks
- View Ruby's status and capabilities through the dashboard

### CLI Interface

```powershell
# Chat with Ruby directly
python -m crystal.cli chat "Hello Ruby, can you help me organize my downloads folder?"

# Get Ruby's status and capabilities
python -m crystal.cli status

# Ask Ruby for system assistance
python -m crystal.cli chat "Can you help me schedule a backup task?"

# View all CLI options
python -m crystal.cli --help
```

## Configuration

Edit `config/settings.py` to customize Ruby's behavior:

- Database connection settings
- AI model preferences (local Ollama vs OpenAI API)
- Ruby's capabilities and permissions
- Web server port and security settings
- File organization preferences

Ruby's personality and instructions can be customized by editing:
`crystal/assistants/instructions/ruby_instructions.md`

## Development

This project follows the architecture outlined in `PROJECT_OVERVIEW.md`. Key design principles:

- **Unified Architecture**: Ruby uses the new `CrystalAssistant` class - a single, clean implementation
- **Instruction-Driven**: Ruby's behavior is defined by instruction files, not hardcoded logic
- **Async-First**: All operations use async/await for optimal performance
- **Type Safety**: Full type hints with Pydantic models for reliability
- **Security**: Authentication and audit logging built-in
- **Extensibility**: The unified Crystal assistant framework makes adding new assistants simple

### Adding New Assistants

When you're ready to add more assistants (like Emerald for coding or Diamond for data analysis):

1. Create an instruction file: `crystal/assistants/instructions/assistant_name_instructions.md`
2. Add configuration in `config/settings.py`  
3. Create a simple class that inherits from `CrystalAssistant`
4. The assistant automatically inherits all functionality from the unified framework

### Ruby's Instructions

Ruby's complete personality and capabilities are defined in:
`crystal/assistants/instructions/ruby_instructions.md`

You can modify this file to change how Ruby behaves, responds, and what tasks she can help with.

## License

MIT License - see LICENSE file for details.
