# 🌍 Real-World Multi-Agent AI Travel Planner

An Agentic AI Travel Planner built with Python, LangGraph, MCP, Groq, PostgreSQL, and Streamlit.

The system accepts a natural-language travel request, intelligently selects the required specialist agents, gathers travel information, creates a draft itinerary, pauses for Human-in-the-Loop (HITL) approval, and then generates a polished final travel plan.

## 🚀 Live Demo

https://agenticaitravelplanner-29kyqdhdshibacjkcdxyuy.streamlit.app/

## 📌 Project Overview

Traditional travel planning requires users to manually search for flights, hotels, weather, transportation, activities, and budget information.

This project automates that workflow using a multi-agent architecture.

The user provides a natural-language request such as:

> Plan a 7-day Japan trip under ₹2 lakh. Prefer budget hotels and avoid overnight travel.

The system then:

1. Understands the user's requirements.
2. Determines which specialist agents are required.
3. Searches for relevant flight information.
4. Searches for hotel and accommodation options.
5. Retrieves weather information when requested.
6. Calculates and evaluates the travel budget.
7. Creates a day-by-day draft itinerary.
8. Pauses for human approval.
9. Revises the itinerary when feedback is provided.
10. Generates the final polished travel plan.

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │      User Request    │
                         │  Natural Language    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Guardrail / Supervisor│
                         │                      │
                         │ Intent + Agent       │
                         │ Selection            │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
       ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
       │ Flight Agent│       │ Hotel Agent │       │Weather Agent│
       └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                              ┌─────▼─────┐
                              │Budget Agent│
                              └─────┬─────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Itinerary Agent    │
                         │                      │
                         │ Draft Day-by-Day Plan│
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Human-in-the-Loop    │
                         │      Approval        │
                         └──────────┬───────────┘
                                    │
                       ┌────────────┴────────────┐
                       │                         │
                    Approved                  Revise
                       │                         │
                       │                    User Feedback
                       │                         │
                       └────────────┬────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  Final Response Agent│
                         │                      │
                         │ Polished Travel Plan │
                         └──────────────────────┘
```

---

# ✨ Key Features

- 🤖 Multi-agent travel planning
- 🧠 LangGraph-based agent orchestration
- 🔀 Dynamic agent selection based on user requirements
- ✈️ Flight information retrieval
- 🏨 Hotel and accommodation research
- 🌦️ Weather and forecast integration
- 💰 Travel budget estimation
- 🗺️ Day-by-day itinerary generation
- 👤 Human-in-the-Loop approval
- 🔄 Itinerary revision using human feedback
- 🧠 Persistent LangGraph state and checkpointing
- 🗄️ PostgreSQL checkpoint database
- 🔌 MCP-based external tool integration
- ⚡ Groq-powered LLM inference
- 🛡️ Rate-limit retry handling
- 🖥️ Streamlit user interface
- ☁️ Streamlit Cloud deployment
- 🔐 Environment and secrets-based API configuration

---

# 🛠️ Tech Stack

## Programming Language

- Python

## AI / LLM

- Groq
- `openai/gpt-oss-20b`
- LangChain
- LangGraph

## Agent Orchestration

- LangGraph
- Multi-agent workflow
- Supervisor-based routing
- Human-in-the-Loop interrupts

## MCP

- Model Context Protocol (MCP)
- Custom Weather MCP
- MCP communication through supported transport mechanisms

## Database

- PostgreSQL
- LangGraph PostgreSQL Checkpointer
- Neon PostgreSQL

## External APIs / Tools

- AviationStack
- Tavily
- OpenWeather
- Custom MCP tools

## Frontend

- Streamlit

## Development

- Git
- GitHub
- Python virtual environment
- python-dotenv

---

# 🧠 Agent Architecture

The application separates responsibilities across specialized agents.

## 1. Supervisor / Guardrail Agent

The Supervisor analyzes the user's travel request and determines which agents are required.

For example:

```text
User:
"Plan a 7-day Japan trip under ₹2 lakh.
Prefer budget hotels and avoid overnight travel."

Supervisor:
- Flight Agent
- Hotel Agent
- Budget Agent
- Itinerary Agent
```

If weather is not requested or required, the Weather Agent can be skipped.

This prevents unnecessary tool calls and keeps the workflow efficient.

---

## 2. Flight Agent

The Flight Agent retrieves flight-related information using the configured flight API or tool.

It focuses on:

- Origin and destination
- Travel dates
- Flight options
- Travel constraints
- Estimated prices when available
- Overnight-travel preferences

The agent passes useful information to the downstream itinerary workflow.

---

## 3. Hotel Agent

The Hotel Agent searches for accommodation information using the configured search tools.

It considers:

- Destination
- Budget
- Preferred hotel type
- Location
- Accommodation options
- Available pricing information

Raw search results are cleaned and formatted before being presented to the user.

---

## 4. Weather Agent

The Weather Agent is invoked when weather information is relevant to the request.

It retrieves:

- Current weather
- Forecast information
- Practical travel and packing considerations

Weather data is obtained through the configured weather MCP integration.

---

## 5. Budget Agent

The Budget Agent evaluates the available travel information and produces a budget-oriented summary.

It considers categories such as:

```text
Flights
Accommodation
Transportation
Food
Activities
Miscellaneous expenses
```

The agent also checks the estimated cost against the user's stated budget.

---

## 6. Itinerary Agent

The Itinerary Agent combines the available information from the specialist agents.

It receives:

```text
User Request
Trip Constraints
Flight Information
Hotel Information
Weather Information
Budget Information
```

It then generates a concise draft itinerary.

The draft intentionally uses a simple day-by-day format so that it is easy for a human to review.

Example:

```text
Day 1 – Arrival

• Flight information
• Airport transfer
• Accommodation
• Evening activity

Day 2 – City Exploration

• Morning activity
• Afternoon activity
• Evening activity
```

---

# 👤 Human-in-the-Loop

One of the key features of the project is the Human-in-the-Loop workflow.

After generating the draft itinerary, LangGraph pauses execution using an interrupt.

The user can select:

```text
Yes
```

or:

```text
No, revise it
```

If the user approves:

```text
Draft Itinerary
      ↓
Human Approval
      ↓
Final Response
```

If the user rejects the draft:

```text
Draft Itinerary
      ↓
Human Feedback
      ↓
Final Response Agent
      ↓
Revised Travel Plan
```

This prevents the system from automatically finalizing a plan without human review.

---

# 🧠 LangGraph Workflow

The workflow is implemented using LangGraph.

Conceptually:

```text
START
  ↓
Supervisor / Guardrail
  ↓
Dynamic Agent Selection
  ↓
Specialist Agents
  ↓
Itinerary Agent
  ↓
Human Approval Interrupt
  ↓
Final Response Agent
  ↓
END
```

The workflow maintains state across the different agents.

---

# 💾 PostgreSQL Checkpointing

The project uses PostgreSQL for LangGraph checkpoint persistence.

This allows the application to maintain state using a conversation or thread identifier.

The application uses:

```text
PostgreSQL
     ↓
LangGraph PostgresSaver
     ↓
Thread-based state persistence
```

The PostgreSQL database is hosted using Neon PostgreSQL.

A thread ID is generated for each session:

```text
demo_user_<unique_id>
```

This allows LangGraph to resume the workflow when required, especially during Human-in-the-Loop execution.

---

# 🔌 MCP Integration

The project demonstrates the use of Model Context Protocol (MCP) for external tool integration.

The weather functionality is exposed through a custom MCP server.

The architecture separates:

```text
Agent
  ↓
MCP Client
  ↓
MCP Tool
  ↓
External API
```

This keeps external service access separated from the agent's core reasoning logic.

---

# 🔐 Environment Variables

Create a `.env` file locally.

Example:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
DATABASE_URL=your_postgresql_connection_string
```

Never commit API keys or database credentials to GitHub.

---

# 📁 Project Structure

```text
Agentic_AI_Travel_Planner/
│
├── agents.py
├── graph.py
├── frontend.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

### Main Files

### `agents.py`

Contains the main specialist agents and LLM-powered processing:

```text
Supervisor
Flight Agent
Hotel Agent
Weather Agent
Budget Agent
Itinerary Agent
Human Approval
Final Response Agent
```

### `graph.py`

Defines the LangGraph workflow and PostgreSQL checkpointer.

### `frontend.py`

Contains the Streamlit application and user interface.

### `config.py`

Handles configuration, environment variables, Streamlit secrets, and Groq LLM initialization.

---

# ⚙️ Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/naman-DA/Agentic_AI_Travel_Planner.git
cd Agentic_AI_Travel_Planner
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create:

```text
.env
```

and add the required API keys and PostgreSQL connection string.

## 5. Run the application

```bash
streamlit run frontend.py
```

The application will start locally at:

```text
http://localhost:8501
```

---

# ☁️ Streamlit Deployment

The project can be deployed using Streamlit Cloud.

Connect the GitHub repository and configure the required secrets.

Example Streamlit secrets:

```toml
GROQ_API_KEY = "your_groq_api_key"
GROQ_MODEL = "openai/gpt-oss-20b"
TAVILY_API_KEY = "your_tavily_api_key"
AVIATIONSTACK_API_KEY = "your_aviationstack_api_key"
OPENWEATHER_API_KEY = "your_openweather_api_key"
DATABASE_URL = "your_postgresql_connection_string"
```

Do not commit these secrets to GitHub.

---

# 🛡️ Rate-Limit Handling

The application includes retry handling for Groq rate-limit errors.

The LLM utility retries temporary `RateLimitError` failures with increasing delays.

Conceptually:

```text
LLM Request
    ↓
429 Rate Limit?
    │
    ├── No → Continue
    │
    └── Yes
          ↓
        Wait
          ↓
        Retry
          ↓
        Retry
          ↓
    Continue / Raise
```

The project also uses a smaller context window for downstream itinerary generation to reduce unnecessary token consumption.

---

# 🎯 Example User Requests

### Example 1

```text
Plan a 7-day Japan trip under ₹2 lakh.
Prefer budget hotels and avoid overnight travel.
```

### Example 2

```text
Plan a 5-day trip to New Zealand with budget accommodation
and include weather information.
```

### Example 3

```text
Plan a budget trip to Japan.
I want cultural attractions, affordable hotels,
and minimal long-distance travel.
```

The Supervisor determines which specialist agents are necessary for each request.

---

# 🔄 Example Workflow

For:

```text
Plan a 7-day Japan trip under ₹2 lakh.
Prefer budget hotels and avoid overnight travel.
```

The system can produce:

```text
User Request
     ↓
Supervisor
     ↓
Flight Agent
     ↓
Hotel Agent
     ↓
Budget Agent
     ↓
Itinerary Agent
     ↓
Human Approval
     ↓
Final Travel Plan
```

If weather is explicitly requested:

```text
User Request
     ↓
Supervisor
     ↓
Flight ─┐
Hotel ─┤
Weather ├──→ Itinerary
Budget ─┘
             ↓
       Human Approval
             ↓
       Final Response
```

---

# 👤 User Interface

The Streamlit interface provides:

- User/session management
- Thread ID
- Travel request input
- Supervisor reasoning
- Selected agents
- Research Results
- Draft Itinerary
- Human Approval
- Feedback input
- Final Travel Plan

Intermediate research results can be expanded when required, while the main interface focuses on the draft and final plan.

---

# 🧪 Testing

The project has been tested with travel requests involving:

- Japan
- New Zealand
- Different trip durations
- Budget constraints
- Hotel preferences
- Overnight-travel constraints
- Requests with and without weather requirements

The workflow supports dynamic agent selection based on the user's request.

---

# 🔒 Security Considerations

The following files and data should never be committed:

```text
.env
.venv/
__pycache__/
.streamlit/secrets.toml
API keys
Database credentials
Private tokens
```

Recommended `.gitignore` entries:

```gitignore
.env
.venv/
__pycache__/
*.pyc
.streamlit/secrets.toml
```

---

# 🚧 Current Limitations

The current system is primarily a travel research and itinerary planning system.

It does not directly complete real-world bookings.

External services may also impose:

- API limits
- Rate limits
- Availability restrictions
- Pricing changes
- Incomplete search results

Therefore, generated prices and availability should be treated as estimates unless confirmed by the respective provider.

---

# 🔮 Future Improvements

Potential future improvements include:

- Real flight booking integration
- Hotel booking integration
- Restaurant recommendations and reservations
- More travel providers
- User authentication
- Persistent user profiles
- Long-term travel preferences
- Streaming agent responses
- More advanced itinerary optimization
- Cost optimization algorithms
- Map integration
- Real-time price tracking
- Notification and alert system
- Redis-based caching
- Production monitoring
- More MCP tools
- Multi-destination optimization

---

# 📊 Why This Project?

This project demonstrates practical implementation of modern Generative AI concepts:

- LLM applications
- Agentic AI
- Multi-agent orchestration
- LangGraph
- LangChain
- MCP
- Tool calling
- External API integration
- Human-in-the-Loop
- State persistence
- PostgreSQL
- Prompt engineering
- Streamlit deployment
- Error handling
- Rate-limit management

Rather than building a simple chatbot, the project demonstrates how multiple specialized AI components can collaborate to solve a real-world planning problem.

---

# 💡 Key Learning Outcomes

Through this project, I worked with:

```text
LLM
 ↓
Prompt Engineering
 ↓
Agent
 ↓
Tool Calling
 ↓
MCP
 ↓
Multi-Agent Orchestration
 ↓
LangGraph State Management
 ↓
Human-in-the-Loop
 ↓
PostgreSQL Checkpointing
 ↓
Streamlit Deployment
```

The project provided practical experience in designing an AI system where the LLM is not responsible for the entire application logic, but instead operates within a controlled workflow with specialized tools, state management, validation, and human supervision.

---

# 👨‍💻 Author

**Naman Garg**

B.Tech Computer Science

GitHub: https://github.com/naman-DA

LinkedIn: https://linkedin.com/in/naman-garg-16672b327

---

# ⭐ Project Highlights

```text
✓ Multi-Agent AI Travel Planner
✓ LangGraph orchestration
✓ MCP integration
✓ Groq LLM
✓ Dynamic agent selection
✓ Flight research
✓ Hotel research
✓ Weather integration
✓ Budget planning
✓ Itinerary generation
✓ Human-in-the-Loop
✓ PostgreSQL checkpointing
✓ Streamlit UI
✓ Cloud deployment
✓ Rate-limit handling
```