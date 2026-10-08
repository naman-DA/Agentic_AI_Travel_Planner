# Agentic AI Travel Planner

A real-world multi-agent AI travel planning system built with **LangGraph, MCP, Groq, PostgreSQL, and Streamlit**.

The system accepts a natural-language travel request and uses specialized AI agents to research flights, hotels, weather, and budget before generating a day-by-day itinerary. A **Human-in-the-Loop (HITL)** step allows the user to approve or revise the generated itinerary before the final response is produced.

## Live Demo

**Streamlit App:**  
https://agenticaitravelplanner-3zjwssjtrfhl9cuj7cwt8b.streamlit.app/

**GitHub Repository:**  
https://github.com/naman-DA/Agentic_AI_Travel_Planner

---

## Features

- Natural-language travel planning
- Multi-agent orchestration with LangGraph
- Supervisor agent for dynamic agent selection
- Flight research using AviationStack MCP integration
- Hotel research using Tavily
- Weather and forecast information using a custom MCP server
- Budget analysis
- Day-by-day itinerary generation
- Human-in-the-Loop itinerary approval and revision
- PostgreSQL-based LangGraph checkpointing
- Persistent conversation/thread state
- Groq LLM integration
- Rate-limit retry handling
- Streamlit web interface
- Cloud deployment using Streamlit Community Cloud

---

## Architecture

```text
                         User
                           |
                           v
                    Streamlit Frontend
                           |
                           v
                    Supervisor Agent
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        Flight Agent   Hotel Agent   Weather Agent
             |             |             |
             v             v             v
       AviationStack     Tavily       Weather MCP
             |             |             |
             +-------------+-------------+
                           |
                           v
                     Budget Agent
                           |
                           v
                   Itinerary Agent
                           |
                           v
                  Human-in-the-Loop
                     /           \
                  Approve       Revise
                     |             |
                     +------+------+
                            |
                            v
                  Final Response Agent
                            |
                            v
                       Final Plan
```

---

## Agent Architecture

### 1. Supervisor Agent

The supervisor analyzes the user's request and determines which specialist agents are required.

It extracts:

- Destination
- Origin
- Duration
- Budget
- Travel style
- Special preferences

It dynamically selects agents such as:

- `flight_agent`
- `hotel_agent`
- `weather_agent`
- `budget_agent`
- `itinerary_agent`

---

### 2. Flight Agent

The flight agent uses AviationStack through MCP to obtain airport and airline information.

It provides flight-related guidance while avoiding unsupported claims about live availability or pricing.

---

### 3. Hotel Agent

The hotel agent uses Tavily search to research:

- Hotels
- Areas to stay
- Accommodation recommendations
- Relevant hotel information

Search results are passed through an LLM formatting step to produce clean travel recommendations.

---

### 4. Weather Agent

The weather agent communicates with the custom weather MCP server to obtain:

- Current weather
- Forecast information
- Travel and packing guidance

The MCP server can communicate through supported MCP transports such as stdio or Streamable HTTP.

---

### 5. Budget Agent

The budget agent analyzes:

- User budget
- Flight information
- Hotel information
- Weather-related considerations

It provides estimated cost categories, risk areas, money-saving suggestions, and overall feasibility.

---

### 6. Itinerary Agent

The itinerary agent combines the available research results and creates a practical day-by-day travel itinerary.

It is instructed to:

- Use only supplied information
- Avoid inventing live travel data
- Include every requested day
- Include transportation and accommodation where available
- Consider budget constraints
- Return clean Markdown

---

## Human-in-the-Loop

Before producing the final response, the itinerary is presented to the user for approval.

The user can:

### Approve

The draft is accepted and passed to the final response agent.

### Request Revision

The user can provide feedback such as:

```text
Increase the budget from ₹2 lakh to ₹4 lakh
and prefer better hotels.
```

The feedback is stored in the LangGraph state and passed to the final response agent.

This allows the system to modify the final travel plan based on human input.

---

## LangGraph Workflow

The workflow follows a state-driven architecture:

```text
START
  |
  v
Supervisor
  |
  +----> Flight Agent
  |
  +----> Hotel Agent
  |
  +----> Weather Agent
  |
  +----> Budget Agent
  |
  v
Itinerary Agent
  |
  v
Human Approval
  |
  +---- Approved ----> Final Response
  |
  +---- Revision ----> Final Response
  |
  v
END
```

LangGraph manages the workflow state and execution between agents.

---

## MCP Integration

The project uses the **Model Context Protocol (MCP)** to connect agents with external tools.

### AviationStack MCP

Used for:

- Airport lookup
- Airline information

### Custom Weather MCP

Used for:

- Current weather
- Weather forecasts

This separates tool communication from the agent logic and makes external capabilities easier to manage.

---

## PostgreSQL Checkpointing

The application uses PostgreSQL with LangGraph's Postgres checkpointer.

This allows the application to maintain graph state across interactions and supports thread-based conversations.

The deployed application uses a PostgreSQL database hosted on Neon.

---

## Technology Stack

| Category | Technologies |
|---|---|
| Language | Python |
| Agent Framework | LangGraph |
| LLM Framework | LangChain |
| LLM | Groq |
| Model | `openai/gpt-oss-20b` |
| Tool Protocol | MCP |
| Database | PostgreSQL |
| Database Hosting | Neon |
| Web UI | Streamlit |
| Flight API | AviationStack |
| Search | Tavily |
| Deployment | Streamlit Community Cloud |
| Version Control | Git, GitHub |

---

## Project Structure

```text
Agentic_AI_Travel_Planner/
│
├── agents.py
├── graph.py
├── state.py
├── config.py
├── mcp_client.py
├── custom_weather_mcp_server.py
├── frontend.py
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Environment Variables

Create a `.env` file locally:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b

TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
OPENWEATHER_API_KEY=your_openweather_api_key

DATABASE_URL=your_postgresql_connection_string
```

For Streamlit Cloud, configure these values using **Streamlit Secrets** instead of committing them to GitHub.

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/naman-DA/Agentic_AI_Travel_Planner.git
cd Agentic_AI_Travel_Planner
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file and add the required API keys and PostgreSQL connection string.

### 5. Run the application

```bash
streamlit run frontend.py
```

The application will open in your browser.

---

## Example Request

```text
Plan a 7-day Japan trip under ₹2 lakh.

I prefer budget hotels, efficient transportation,
and no overnight flights.
```

The system analyzes the request, selects the required agents, researches the trip, creates a draft itinerary, and asks the user for approval.

The user can then revise the plan through the HITL interface.

---

## Example HITL Revision

```text
Increase the budget to ₹4 lakh
and prefer better hotels.
```

The final response agent uses the human feedback when generating the revised travel plan.

---

## Rate-Limit Handling

The project includes retry handling for Groq rate-limit errors.

The LLM invocation retries up to three times with increasing delays when a `RateLimitError` occurs.

This helps prevent temporary API rate limits from immediately terminating the workflow.

---

## Error Handling

The system includes handling for:

- LLM rate limits
- Missing API data
- Unavailable external information
- Unsupported live flight information
- Missing travel data
- Invalid travel requests through the supervisor guardrail

Agents are instructed not to invent unsupported live travel information.

---

## Deployment

The application is deployed using Streamlit Community Cloud.

Live application:

```text
https://agenticaitravelplanner-3zjwssjtrfhl9cuj7cwt8b.streamlit.app/
```

Sensitive API keys and database credentials are configured through Streamlit Secrets.

---

## Security

Secrets are not stored directly in the source code.

The project uses:

- `.env` for local development
- Streamlit Secrets for cloud deployment
- `.gitignore` to prevent accidental secret commits

Never commit:

```text
.env
API keys
Database passwords
Private credentials
```

---

## Limitations

- Flight information depends on the available AviationStack API data.
- Hotel recommendations depend on Tavily search results.
- Travel prices can change and should be verified before booking.
- The system provides planning assistance rather than direct booking.
- External API availability can affect the quality of generated recommendations.
- LLM output depends on the quality and completeness of retrieved information.

---

## Future Improvements

Potential future improvements include:

- Real-time flight search and price comparison
- Hotel booking integration
- Restaurant recommendations
- Map-based itinerary visualization
- Currency conversion
- Calendar integration
- User authentication
- Trip history and saved itineraries
- More specialized travel agents
- Production-grade observability
- Streaming agent responses

---

## Why This Project?

This project demonstrates how modern AI applications can move beyond a simple chatbot architecture.

It combines:

- LLMs
- Multi-agent systems
- LangGraph
- MCP
- Tool calling
- External APIs
- Retrieval and research
- Persistent state
- Human-in-the-Loop workflows
- PostgreSQL checkpointing
- Cloud deployment

The architecture is designed around specialized agents rather than placing the entire travel-planning workflow inside a single LLM prompt.

---

## Learning Outcomes

Through this project, I gained practical experience with:

- Multi-agent AI architecture
- LangGraph state management
- Supervisor-based agent orchestration
- MCP-based tool integration
- Human-in-the-Loop workflows
- PostgreSQL checkpointing
- LLM prompt design
- External API integration
- Error and rate-limit handling
- Streamlit deployment
- Building production-oriented GenAI applications

---

## Author

**Naman Garg**

B.Tech Computer Science Engineering

GitHub:  
https://github.com/naman-DA

LinkedIn:  
https://www.linkedin.com/in/naman-garg-16672b327

---

## Project Highlights

**Agentic AI Travel Planner**

- Multi-agent travel planning system
- LangGraph-based orchestration
- MCP-based external tool integration
- PostgreSQL persistent checkpointing
- Human-in-the-Loop itinerary revision
- Groq-powered LLM
- Streamlit web application
- Deployed and publicly accessible