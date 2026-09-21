# Agentic AI Travel Planner

A real-world multi-agent travel planning system built with Python, LangGraph, LangChain, MCP, Groq, PostgreSQL, and Streamlit.

The system accepts natural-language travel requests and coordinates specialized AI agents for flights, hotels, weather, budgeting, and itinerary generation. It uses Model Context Protocol (MCP) to connect agents with external tools and supports PostgreSQL checkpointing, multi-turn state management, and Human-in-the-Loop approval.

## Features

- Multi-agent travel planning with LangGraph
- Supervisor-based agent routing
- Flight information through AviationStack MCP
- Hotel and travel research through Tavily MCP
- Current weather and forecast through custom Weather MCP
- Budget analysis and feasibility assessment
- Day-by-day itinerary generation
- Human-in-the-Loop itinerary approval
- Itinerary revision based on human feedback
- PostgreSQL checkpointing for persistent LangGraph state
- Thread-based multi-turn conversations
- Groq LLM integration
- Streamlit interactive frontend
- MCP integration using stdio and Streamable HTTP

## Architecture

User
  |
  v
Streamlit Frontend
  |
  v
LangGraph
  |
  v
Supervisor Agent
  |
  +------------------+------------------+
  |                  |                  |
  v                  v                  v
Flight Agent      Hotel Agent      Weather Agent
  |                  |                  |
  v                  v                  v
AviationStack      Tavily MCP       Weather MCP
MCP
  |                  |                  |
  +------------------+------------------+
                     |
                     v
               Budget Agent
                     |
                     v
              Itinerary Agent
                     |
                     v
              Human Approval
                 /       \
             Approve     Revise
                |          |
                +----+-----+
                     |
                     v
          Final Response Agent
                     |
                     v
              Final Travel Plan

## Multi-Agent Workflow

### 1. Supervisor Agent

The supervisor receives the user's travel request and determines which specialist agents are required.

It extracts travel constraints such as:

- Destination
- Origin
- Duration
- Budget
- Travel style
- Special preferences

It then routes the request to the appropriate specialist agents.

### 2. Flight Agent

The Flight Agent uses the AviationStack MCP server to access aviation-related tools.

It can work with information such as:

- Airports
- Airlines
- Aviation-related data

The agent is instructed not to fabricate live flight availability or prices when the external API does not provide them.

### 3. Hotel Agent

The Hotel Agent uses Tavily MCP to research:

- Hotels
- Areas to stay
- Accommodation options
- Travel-related information

### 4. Weather Agent

The Weather Agent uses the custom Weather MCP server to retrieve:

- Current weather
- Temperature
- Feels-like temperature
- Humidity
- Weather condition
- Wind speed
- Forecast information

### 5. Budget Agent

The Budget Agent analyzes the collected travel information and generates:

- Estimated cost categories
- Budget feasibility
- Risk areas
- Money-saving suggestions

### 6. Itinerary Agent

The Itinerary Agent combines the specialist-agent outputs and generates a practical day-by-day travel itinerary containing:

- Accommodation
- Transportation
- Activities
- Budget considerations
- Daily schedule

### 7. Human-in-the-Loop

The generated itinerary is paused for human approval using LangGraph's interrupt mechanism.

The user can either approve the itinerary or provide feedback for revision.

Approve:

Draft Itinerary
      |
      v
Human Approval
      |
      v
Final Response

Revise:

Draft Itinerary
      |
      v
Human Feedback
      |
      v
Final Response

This allows the user to modify requirements such as budget, travel preferences, accommodation style, or other constraints before the final response is generated.

### 8. Final Response Agent

The Final Response Agent generates the final user-ready travel plan using the approved itinerary and human feedback.

## MCP Architecture

This project integrates multiple MCP servers.

### Tavily MCP

Transport:

Streamable HTTP

The AI application connects to Tavily MCP through LangChain MCP adapters.

AI Agent
  |
  v
LangChain MCP Adapter
  |
  v
Tavily MCP
  |
  v
Travel/Web Search

### AviationStack MCP

Transport:

stdio

AviationStack MCP is intentionally maintained as a separate external installation and is not included inside this repository.

AI Agent
  |
  v
LangChain MCP Adapter
  |
  v
AviationStack MCP
  |
  v
AviationStack API

The path to the AviationStack MCP Python environment is configured through the environment variable:

AVIATION_MCP_PYTHON

### Custom Weather MCP

Transport:

stdio

The project contains:

custom_weather_mcp_server.py

The server exposes:

- get_current_weather
- get_forecast

AI Agent
  |
  v
LangChain MCP Adapter
  |
  v
Custom Weather MCP
  |
  v
OpenWeather API

## Project Structure

Agentic_AI_Travel_Planner/
|
+-- agents.py
+-- graph.py
+-- state.py
+-- mcp_client.py
+-- config.py
+-- custom_weather_mcp_server.py
+-- frontend.py
|
+-- requirements.txt
+-- .env.example
+-- .gitignore
+-- README.md

The AviationStack MCP installation remains outside the repository:

MULTI_AGENT_SYSTEM_WITH_MCP/
|
+-- aviationstack-mcp/
    |
    +-- .venv/

The AviationStack MCP virtual environment is not committed to GitHub.

## Tech Stack

### AI / Agentic AI

- Python
- LangGraph
- LangChain
- Groq
- LangChain MCP Adapters
- Model Context Protocol (MCP)

### MCP

- Tavily MCP
- AviationStack MCP
- Custom Weather MCP

### Database

- PostgreSQL
- LangGraph PostgreSQL Checkpointer
- psycopg

### Frontend

- Streamlit

### External APIs

- Tavily
- AviationStack
- OpenWeather

## Installation

### 1. Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Agentic_AI_Travel_Planner

### 2. Create a virtual environment

Windows:

python -m venv .venv

Activate:

.venv\Scripts\activate

Linux/macOS:

python3 -m venv .venv
source .venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

## AviationStack MCP Setup

AviationStack MCP is installed separately from this repository.

The AI application connects to the existing AviationStack MCP installation through the environment variable:

AVIATION_MCP_PYTHON

Example on Windows:

AVIATION_MCP_PYTHON=C:\path\to\aviationstack-mcp\.venv\Scripts\python.exe

The AviationStack MCP environment should not be committed to GitHub.

## Environment Variables

Create a local .env file using .env.example as a template.

Example:

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b

TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
OPENWEATHER_API_KEY=your_openweather_api_key

DATABASE_URL=your_postgresql_connection_string

AVIATION_MCP_PYTHON=path_to_aviationstack_mcp_python

Never commit .env to GitHub.

## PostgreSQL Checkpointing

The project uses LangGraph's PostgreSQL checkpointer for persistent graph state.

Configure the database connection using:

DATABASE_URL=your_postgresql_connection_string

When DATABASE_URL is available, the graph initializes the PostgreSQL checkpointer.

This allows the application to maintain thread-based state and resume Human-in-the-Loop workflows.

## Running the Application

Activate the virtual environment:

.venv\Scripts\activate

Run Streamlit:

streamlit run frontend.py

The application will open in the browser.

## Example User Request

Plan a 7-day trip to Japan from Delhi under ₹2 lakh.

Preferences:

- Budget hotels
- No overnight flights
- Local transportation
- Popular attractions
- Practical day-by-day itinerary

The supervisor analyzes the request and routes the work to the required specialist agents.

## Example Workflow

User Request
    |
    v
Input Guardrail
    |
    v
Supervisor
    |
    +--> Flight Agent
    |
    +--> Hotel Agent
    |
    +--> Weather Agent
    |
    +--> Budget Agent
    |
    v
Itinerary Agent
    |
    v
Human Approval
    |
    +--> Approved
    |       |
    |       v
    |   Final Response
    |
    +--> Feedback
            |
            v
       Revised Response

## State Management

The LangGraph state contains information including:

- user_query
- user_id
- trip_constraints
- selected_agents
- supervisor_reasoning
- flight_results
- hotel_results
- weather_results
- budget_results
- itinerary
- approval_request
- human_feedback
- approved
- final_response
- llm_calls

PostgreSQL checkpointing allows this state to persist between interactions.

## Human-in-the-Loop Example

The system first generates a draft itinerary.

The user can then review the draft and provide feedback.

For example:

Initial request:

Plan a 7-day Japan trip under ₹2 lakh.

After reviewing the itinerary, the user can provide feedback such as:

Increase the budget to ₹5 lakh and make the trip more premium.

The system can then use the human feedback to generate the revised final travel plan.

## Design Principles

The project follows production-oriented design principles:

- Agents focus on reasoning and orchestration.
- External services are accessed through tools and MCP.
- API credentials are stored in environment variables.
- MCP servers are separated from core agent logic.
- Graph state is explicitly defined.
- Human approval is implemented using LangGraph interrupts.
- PostgreSQL is used for persistent graph state.
- Live information is not fabricated when external tools cannot provide it.
- MCP server installations can remain independent from the main application.

## Security

Do not commit:

- .env
- API keys
- PostgreSQL credentials
- Virtual environments
- MCP virtual environments
- node_modules
- Python cache files

The repository includes a .gitignore to prevent these files from being committed.

## Current MCP Connections

The project currently uses:

1. Tavily MCP
   - Transport: Streamable HTTP
   - Purpose: Web/travel research

2. AviationStack MCP
   - Transport: stdio
   - Purpose: Aviation information
   - Installation: External

3. Custom Weather MCP
   - Transport: stdio
   - Purpose: Current weather and forecast
   - API: OpenWeather

## Example Output

The application can generate a complete travel plan containing:

- Supervisor reasoning
- Selected agents
- Flight guidance
- Hotel research
- Current weather
- Forecast
- Budget assessment
- Risk areas
- Money-saving suggestions
- Day-by-day itinerary
- Transportation recommendations
- Booking guidance
- Final approved travel plan

## Project Highlights

This project demonstrates practical implementation of:

LLM
 |
 +-- Agentic AI
 |
 +-- Multi-Agent Orchestration
 |
 +-- LangGraph
 |
 +-- MCP
 |     |
 |     +-- Streamable HTTP
 |     |
 |     +-- stdio
 |
 +-- Tool Calling
 |
 +-- Human-in-the-Loop
 |
 +-- Persistent State
 |
 +-- PostgreSQL Checkpointing
 |
 +-- External API Integration

## Future Improvements

- Flight booking integration
- Hotel booking integration
- User authentication
- Persistent user profiles
- Redis caching
- Production API layer
- Docker deployment
- Cloud deployment
- Streaming agent responses
- Additional travel MCP servers
- Automatic PDF itinerary generation
- Additional travel providers

## Author

Naman Garg

B.Tech - Computer Science Engineering

GitHub: https://github.com/naman-DA

LinkedIn: https://www.linkedin.com/in/naman-garg-16672b327/