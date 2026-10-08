import asyncio
import json
import re
import time
from groq import RateLimitError
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
from langgraph.types import interrupt
from config import get_llm
from mcp_client import (
    tavily_mcp_search,
    aviation_mcp_call,
    weather_mcp_search,
    forecast_mcp_search
)
from state import TravelState
llm=get_llm()

def _llm_text(system:str,prompt:str)->str:
    for attempt in range(3):
        try:
            response=llm.invoke(
                [
                    SystemMessage(content=system),
                    HumanMessage(content=prompt)
                ]
            )
            return re.sub(r"<[^>]+>"," ",response.content).strip()
        except RateLimitError:
            if attempt==2:
                raise
            time.sleep(4*(attempt+1))

def _json_from_llm(text:str)->dict:
    print("\n========== RAW LLM RESPONSE ==========")
    print(text)
    print("======================================\n")
    start=text.index("{")
    end=text.rindex("}")+1
    json_text=text[start:end]
    print("\n========== EXTRACTED JSON ==========")
    print(json_text)
    print("====================================\n")
    return json.loads(json_text)

def supervisor_agent(state:TravelState):
    query=state["user_query"]
    guardrail_prompt=f"""
Determine whether the following request is a valid travel planning request.
Return only JSON in this format:
{{
    "allowed": true,
    "reason": ""
}}
User request:
{query}
"""
    guardrail_raw=_llm_text(
        "You are an input validation guardrail. Return strict JSON only.",
        guardrail_prompt
    )
    print("\n========== GUARDRAIL RAW RESPONSE ==========")
    print(guardrail_raw)
    print("============================================\n")
    guardrail_result=_json_from_llm(guardrail_raw)
    print("\n========== GUARDRAIL PARSED RESPONSE ==========")
    print(json.dumps(guardrail_result,indent=2))
    print("================================================\n")
    if not guardrail_result.get("allowed",False):
        reason=guardrail_result.get(
            "reason",
            "Request rejected by input guardrail."
        )
        return {
            "selected_agents":[],
            "trip_constraints":{},
            "supervisor_reasoning":reason,
            "final_response":reason,
            "messages":[
                AIMessage(content=f"Guardrail blocked request: {reason}")
            ],
            "llm_calls":state.get("llm_calls",0)+1
        }
    prompt=f"""
You are the supervisor of a real-world multi-agent travel planning system.
Decide which specialist agents are needed for this user request.
Available agents:
- flight_agent: use when flights, airports, airlines, routes, or airfare guidance are needed
- hotel_agent: use when hotels, stays, neighborhoods, or accommodation are needed
- weather_agent: use when weather, climate, season, packing, or forecast is useful
- budget_agent: use when budget, affordability, cost, or price constraints are mentioned
- itinerary_agent: almost always needed to produce the travel plan
Return only JSON with this schema:
{{
  "selected_agents": ["flight_agent","hotel_agent","weather_agent","budget_agent","itinerary_agent"],
  "trip_constraints": {{
    "destination": "",
    "origin": "",
    "duration": "",
    "budget": "",
    "travel_style": "",
    "special_preferences": []
  }},
  "reasoning": ""
}}
User request:
{query}
"""
    raw=_llm_text(
        "You route work to specialist agents. Return strict JSON only.",
        prompt
    )
    print("\n========== RAW LLM RESPONSE ==========")
    print(raw)
    print("======================================\n")
    parsed=_json_from_llm(raw)
    print("\n========== PARSED JSON ==========")
    print(json.dumps(parsed,indent=2))
    print("=================================\n")
    selected=parsed["selected_agents"]
    return {
        "selected_agents":selected,
        "trip_constraints":parsed["trip_constraints"],
        "supervisor_reasoning":parsed["reasoning"],
        "messages":[
            AIMessage(content="Supervisor created the agent plan.")
        ],
        "llm_calls":state.get("llm_calls",0)+1
    }

def flight_agent(state:TravelState):
    query=state["user_query"]
    constraints=state["trip_constraints"]
    destination=constraints["destination"]
    print("\n========== FLIGHT AGENT INPUT ==========")
    print("Query:",query)
    print("Constraints:",constraints)
    print("========================================\n")
    airports=asyncio.run(
        aviation_mcp_call(
            "list_airports",
            {
                "search":destination,
                "limit":10
            }
        )
    )
    airlines=asyncio.run(
        aviation_mcp_call(
            "list_airlines",
            {
                "search":"",
                "limit":10
            }
        )
    )
    print("\n========== AIRPORT MCP DATA ==========")
    print(airports)
    print("======================================\n")
    print("\n========== AIRLINE MCP DATA ==========")
    print(airlines)
    print("======================================\n")
    airport_text=str(airports)[:2000]
    airline_text=str(airlines)[:2000]
    prompt=f"""
Create concise flight guidance for this trip.
User request:
{query}
Trip constraints:
{constraints}
Airport MCP data:
{airport_text}
Airline MCP data:
{airline_text}
Rules:
- Use the MCP data when available.
- Do not invent live flight availability.
- Do not invent flight prices or fares.
- Do not claim a specific flight exists unless the MCP data supports it.
- If the MCP data reports an API restriction or unavailable data, clearly state that flight data is unavailable.
- You may provide general booking guidance when live data is unavailable.
- Keep the response under 500 words.
"""
    result=_llm_text(
        "You are a flight planning specialist. Never invent live flight data.",
        prompt
    )
    print("\n========== FLIGHT AGENT OUTPUT ==========")
    print(result)
    print("=========================================\n")
    return {
        "flight_results":result,
        "messages":[
            AIMessage(content="Flight agent completed.")
        ],
        "llm_calls":state.get("llm_calls",0)+1
    }

def hotel_agent(state:TravelState):
    query=f"Best hotels and areas to stay for: {state['user_query']}"
    print("\n========== HOTEL AGENT INPUT ==========")
    print(query)
    print("=======================================\n")
    result=asyncio.run(
        tavily_mcp_search(query)
    )
    clean_result=re.sub(r"<[^>]+>"," ",str(result))
    clean_result=re.sub(r"\s+"," ",clean_result).strip()
    print("\n========== HOTEL SEARCH RESULT ==========")
    print(clean_result)
    print("=========================================\n")
    prompt=f"""
Create concise hotel and accommodation recommendations using only the supplied search results.
User request:
{state["user_query"]}
Search results:
{clean_result[:6000]}
Rules:
- Use only information contained in the supplied search results.
- Do not invent hotel names, prices, ratings, locations, availability, or amenities.
- If specific information is unavailable, say so.
- Summarize the useful accommodation information for the user.
- Do not include raw JSON, dictionaries, tool metadata, URLs as raw tool output, or search-result metadata.
- Return clean Markdown suitable for a travel planning application.
- Keep the response concise.
"""
    formatted_result=_llm_text(
        "You are a hotel research specialist. Convert supplied search results into clean, factual travel recommendations without adding unsupported information.",
        prompt
    )
    print("\n========== HOTEL AGENT OUTPUT ==========")
    print(formatted_result)
    print("=======================================\n")
    return {
        "hotel_results":formatted_result,
        "messages":[
            AIMessage(content="Hotel agent completed.")
        ],
        "llm_calls":state.get("llm_calls",0)+1
    }

def weather_agent(state:TravelState):
    constraints=state["trip_constraints"]
    city=constraints["destination"]
    print("\n========== WEATHER AGENT INPUT ==========")
    print("City:",city)
    print("=========================================\n")
    weather_data=asyncio.run(
        weather_mcp_search(city)
    )
    forecast_data=asyncio.run(
        forecast_mcp_search(city)
    )
    print("\n========== CURRENT WEATHER ==========")
    print(weather_data)
    print("=====================================\n")
    print("\n========== WEATHER FORECAST ==========")
    print(forecast_data)
    print("======================================\n")
    prompt=f"""
Create a concise weather and packing summary using only the supplied weather data.
Destination:
{city}
Current weather:
{str(weather_data)[:4000]}
Forecast:
{str(forecast_data)[:4000]}
Rules:
- Use only the supplied weather data.
- Do not invent temperatures, dates, conditions, forecasts, or other weather facts.
- Clearly distinguish current weather from forecast information.
- Include practical packing advice only when supported by the supplied conditions.
- Do not include raw JSON, dictionaries, tool metadata, or API response structures.
- Return clean Markdown suitable for a travel planning application.
- Keep the response concise.
"""
    result=_llm_text(
        "You are a weather travel specialist. Convert supplied weather data into a clean factual travel summary without adding unsupported information.",
        prompt
    )
    print("\n========== WEATHER AGENT OUTPUT ==========")
    print(result)
    print("==========================================\n")
    return {
        "weather_results":result,
        "messages":[
            AIMessage(content="Weather agent completed.")
        ],
        "llm_calls":state.get("llm_calls",0)+1
    }

def budget_agent(state:TravelState):
    print("\n========== BUDGET AGENT INPUT ==========")
    print("Trip Constraints:")
    print(state.get("trip_constraints"))
    print("\nFlight Results:")
    print(state.get("flight_results"))
    print("\nHotel Results:")
    print(state.get("hotel_results"))
    print("\nWeather Results:")
    print(state.get("weather_results"))
    print("=========================================\n")
    prompt=f"""
Analyze whether this trip plan is realistic for the user's budget.
User request:
{state['user_query']}
Constraints:
{state.get('trip_constraints',{})}
Flight results:
{state.get('flight_results','')}
Hotel results:
{state.get('hotel_results','')}
Weather results:
{state.get('weather_results','')}
Return a concise budget assessment with:
1. estimated cost categories
2. risk areas
3. money-saving suggestions
4. whether the plan seems feasible
"""
    result=_llm_text(
        "You are a practical travel budget analyst.",
        prompt
    )
    print("\n========== BUDGET AGENT OUTPUT ==========")
    print(result)
    print("=========================================\n")
    return {
        "budget_results":result,
        "messages":[
            AIMessage(content="Budget agent completed.")
        ],
        "llm_calls":state.get("llm_calls",0)+1
    }

def itinerary_agent(state: TravelState):
    flight_results = str(state.get("flight_results", ""))[:1200]
    hotel_results = str(state.get("hotel_results", ""))[:1000]
    weather_results = str(state.get("weather_results", ""))[:700]
    budget_results = str(state.get("budget_results", ""))[:1000]
    prompt = f"""
Create a practical travel itinerary using only the information provided below.
User request:
{state["user_query"]}
Trip constraints:
{state.get("trip_constraints", {})}
Flight information:
{flight_results}
Hotel information:
{hotel_results}
Weather information:
{weather_results}
Budget information:
{budget_results}
Rules:
- Do not invent live flight availability, prices, hotels, weather, or other factual data.
- If information is unavailable, clearly say so.
- Do not use outdated dates unless they are explicitly provided by the user.
- Keep the itinerary concise and practical.
-For a 5-day trip, use exactly Day 1 through Day 5. Do not create Day 0 unless the user explicitly requests an arrival/departure day.
- Create a day-by-day plan.
- Include transportation, accommodation, activities, and budget considerations when available.
- Return clean Markdown only.
- Do not use LaTeX or escaped Markdown.
- Do not output raw JSON, Python dictionaries, tool metadata, or code fences.
- Do not use tables.
- Use simple Markdown headings and bullet points for each day.
- Include every day of the requested trip.
- Do not stop early or omit remaining days.
- Keep the draft concise, around 300-400 words.
"""
    result = _llm_text(
        "You are an expert travel itinerary planner. Use only supplied information.",
        prompt,
    )
    approval_request = f"""
Please review this draft travel plan.
{result}
Reply with approval or feedback.
"""
    return {
        "itinerary": result,
        "approval_request": approval_request,
        "messages": [AIMessage(content="Draft itinerary created for human review.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }

def human_approval_agent(state:TravelState):
    feedback=interrupt(
        {
            "question":"Do you approve this itinerary?",
            "draft_itinerary":state.get("itinerary",""),
            "approval_request":state.get("approval_request",""),
            "expected_response":{
                "approved":True,
                "feedback":"Optional feedback for revision"
            }
        }
    )
    approved=feedback["approved"]
    human_feedback=feedback["feedback"]
    return {
        "approved":approved,
        "human_feedback":human_feedback,
        "messages":[
            AIMessage(content="Human approval step completed.")
        ]
    }

def final_response_agent(state:TravelState):
    print("\n========== FINAL AGENT INPUT ==========")
    print("Approved:",state.get("approved"))
    print("Feedback:",state.get("human_feedback"))
    print("=======================================\n")
    if state["approved"]:
        prompt=f"""
The human approved this draft itinerary.
Produce the final polished travel plan.
Draft itinerary:
{state['itinerary']}
Budget notes:
{state['budget_results']}
Rules:
- Return clean Markdown only.
- Do not use LaTeX or escaped Markdown.
- Do not output raw JSON, Python dictionaries, tool metadata, or code fences.
- Include every day of the requested trip.
- Do not stop early or omit remaining days.
- Keep the response under 700 words.
"""
    else:
        prompt=f"""
The human did not approve the draft.
Original user request:
{state['user_query']}
Draft itinerary:
{state['itinerary']}
Human feedback:
{state['human_feedback']}
Budget notes:
{state['budget_results']}
Rules:
- Return clean Markdown only.
- Do not use LaTeX or escaped Markdown.
- Do not output raw JSON, Python dictionaries, tool metadata, or code fences.
- Include every day of the requested trip.
- Do not stop early or omit remaining days.
- Keep the response under 700 words.
"""
    result=_llm_text(
        "You produce final user-ready travel plans.",
        prompt
    )
    print("\n========== FINAL RESPONSE ==========")
    print(result)
    print("====================================\n")
    return {
        "final_response":result,
        "messages":[
            AIMessage(content=result)
        ],
        "llm_calls":state.get("llm_calls",0)+1
    }
