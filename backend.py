
# ============================================================
# 1. IMPORTS & ENVIRONMENT SETUP
# ============================================================

import os
# os module ka use environment variables read/set karne ke liye hota hai.
# Example: GROQ_API_KEY, DATABASE_URL etc.

import certifi
# certifi trusted SSL certificates provide karta hai.
# HTTPS connections ko secure banane mein help karta hai.

from dotenv import load_dotenv
# .env file ke andar stored variables ko load karne ke liye.
# Example:
# GROQ_API_KEY=your_api_key
# DATABASE_URL=your_database_url


load_dotenv()
# .env file se environment variables load ho jayenge.
# Ab os.getenv() ke through unhe read kar sakte hain.


os.environ["SSL_CERT_FILE"] = certifi.where()
# SSL_CERT_FILE mein trusted CA certificates ka path set kar rahe hain.
# Isse kuch HTTPS/SSL connection issues solve ho sakte hain.

os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
# Requests library ko trusted certificate bundle ka path dete hain.
# External APIs ke HTTPS requests mein help karta hai.


# ============================================================
# 2. PYTHON STANDARD LIBRARY IMPORTS
# ============================================================

from typing import TypedDict, Annotated
# TypedDict:
# State ka structure define karne ke liye use hota hai.
#
# Annotated:
# Kisi type ke saath extra information/metadata attach kar sakte hain.
# LangGraph mein reducers define karne ke liye use hota hai.


import operator
# operator.add ko LangGraph mein reducer ke roop mein use karenge.
# Messages ki lists ko merge karne mein help karega.


import uuid
# Unique IDs generate karne ke liye.
# Hum har new conversation ko unique thread_id de sakte hain.


# ============================================================
# 3. POSTGRESQL IMPORTS
# ============================================================

import psycopg
# PostgreSQL database se connection establish karne ke liye.
# Checkpointer ke data ko PostgreSQL mein save karenge.


from psycopg.rows import dict_row
# Database se rows ko dictionary format mein return karne ke liye.
# Isse database results ko access karna easy hota hai.


# ============================================================
# 4. LANGGRAPH IMPORTS
# ============================================================

from langgraph.graph import StateGraph, START, END
# StateGraph:
# Graph ka structure/building blocks banane ke liye.
#
# START:
# Graph ka starting point.
#
# END:
# Graph ka ending point.


from langgraph.checkpoint.postgres import PostgresSaver
# PostgreSQL-based checkpointer.
# Graph ke checkpoints ko database mein save karne ke liye.
# Isse conversation state ko persist kar sakte hain.


# ============================================================
# 5. LANGCHAIN MESSAGE IMPORTS
# ============================================================

from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
# HumanMessage:
# User ka message represent karta hai.
#
# AIMessage:
# AI/agent ka response represent karta hai.
#
# SystemMessage:
# LLM ko role/instructions dene ke liye.
#
# AnyMessage:
# Different message types ke liye generic type.


# ============================================================
# 6. LLM & CUSTOM TOOLS
# ============================================================

from langchain_groq import ChatGroq
# Groq ke through LLM use karne ke liye LangChain integration.


from tools.tavily_tool import tavily_search
# Custom Tavily search function.
# Hotel information/search results lene ke liye use karenge.


from tools.flight_tool import search_flights
# Custom flight search function.
# User ki query ke according flight data fetch karega.


# ============================================================
# 7. DATABASE URL FUNCTION
# ============================================================

def get_database_url():
    # Ye function database URL read karke return karega.

    database_url = os.getenv("DATABASE_URL")
    # Environment variables se DATABASE_URL read kar rahe hain.
    # Usually ye .env file ke andar stored hota hai.


    if not database_url:
        # Agar DATABASE_URL missing ya empty hai,
        # toh database connection establish nahi kar sakte.

        raise ValueError(
            "DATABASE_URL is missing. Please add your Render PostgreSQL External Database URL to .env"
        )
        # ValueError raise karke clear error message denge.
        # Program ko invalid/missing URL ke saath aage nahi chalne denge.


    if "sslmode=" not in database_url:
        # Check kar rahe hain ki URL mein sslmode already present hai ya nahi.
        # PostgreSQL SSL connection ke liye use hota hai.

        separator = "&" if "?" in database_url else "?"
        # Agar URL mein pehle se query parameters hain (?) toh & use karo.
        # Agar nahi hain toh ? use karo.
        #
        # Example:
        # URL?param=value  -> URL?param=value&sslmode=require
        # URL              -> URL?sslmode=require


        database_url = f"{database_url}{separator}sslmode=require"
        # URL ke end mein SSL requirement add kar rahe hain.
        # Render PostgreSQL connection ko SSL ke saath establish karne ke liye.


    return database_url
    # Final database URL return kar do.


# ============================================================
# 8. GROQ API KEY
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# .env se Groq API key read kar rahe hain.
# LLM ko authenticate karne ke liye API key chahiye.


if not GROQ_API_KEY:
    # Agar API key missing hai toh error raise karo.

    raise ValueError(
        "GROQ_API_KEY is missing. Please add it to your .env file."
    )
    # Clear message milega ki .env mein API key add karni hai.


# ============================================================
# 9. LLM CONFIGURATION
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY
)
# ChatGroq ka LLM object create kar rahe hain.
#
# model:
# Kaunsa language model use karna hai.
#
# api_key:
# Groq API ko authenticate karne ke liye.
#
# Baad mein llm.invoke() ke through LLM ko prompt bhejenge.


# ============================================================
# 10. STATE DEFINITION
# ============================================================

class TravelState(TypedDict):
    # Ye graph ki shared state ka structure hai.
    # Graph ke different nodes isi state ko read/update karenge.


    messages: Annotated[list[AnyMessage], operator.add]
    # messages:
    # Conversation ke saare messages store honge.
    #
    # list[AnyMessage]:
    # HumanMessage, AIMessage etc. ki list.
    #
    # operator.add:
    # Jab node naye messages return karega,
    # toh purani messages list ke saath append/merge hongi.
    #
    # Example:
    # Old: [HumanMessage("Hello")]
    # New: [AIMessage("Hi")]
    # Result: [HumanMessage("Hello"), AIMessage("Hi")]


    user_query: str
    # User ne jo travel-related question poocha hai.
    # Example: "Plan a trip to Goa for 3 days"


    flight_results: str
    # Flight search se aane wale results store honge.


    hotel_results: str
    # Hotel search se aane wale results store honge.


    itinerary: str
    # LLM se generate hua complete travel plan store hoga.


    llm_calls: int
    # Kitni baar LLM/tool agent-related calls count karni hain,
    # uske liye counter.


# ============================================================
# 11. FLIGHT AGENT
# ============================================================

def flight_agent(state: TravelState):
    # Flight agent ko current graph state milegi.
    # State se user query read karke flights search karega.


    query = state["user_query"]
    # Shared state se user ki original query nikal rahe hain.
    #
    # Example:
    # "Find flights from Bangalore to Delhi"


    flight_data = search_flights(query)
    # Custom flight search function call kar rahe hain.
    # Query ko flight tool mein pass karenge.
    #
    # Important:
    # Actual API call aur returned data
    # search_flights() function ke implementation par depend karega.


    return {
        "flight_results": flight_data,
        # Search se mila flight data state mein save kar rahe hain.


        "messages": [
            AIMessage(content="Flight results fetched.")
        ],
        # Graph ki messages list mein ek AI message add kar rahe hain.
        # Isse pata chalta hai ki flight agent ka step complete hua.


        "llm_calls": state.get("llm_calls", 0) + 1
        # Current llm_calls value read kar rahe hain.
        # Agar value missing hai toh 0 le lenge.
        # Phir 1 increment kar rahe hain.
        #
        # Note:
        # Ye counter flight search call ko count kar raha hai,
        # zaroori nahi ki actual LLM call ho.
    }


# ============================================================
# 12. HOTEL AGENT
# ============================================================

def hotel_agent(state: TravelState):
    # Hotel agent shared state se user ki query read karega.


    query = f"Best hotels for {state['user_query']}"
    # Original query ke aage "Best hotels for" add kar rahe hain.
    #
    # Example:
    # Original: Plan a trip to Goa
    # New: Best hotels for Plan a trip to Goa


    hotel_results = tavily_search(query)
    # Tavily search tool ko call kar rahe hain.
    # Search results ko hotel_results variable mein store karenge.


    return {
        "hotel_results": hotel_results,
        # Hotel search ka result state mein save kar rahe hain.


        "messages": [
            AIMessage(content="Hotel information fetched.")
        ],
        # Messages list mein hotel agent ka status add kar rahe hain.


        "llm_calls": state.get("llm_calls", 0) + 1
        # Counter ko 1 se increment kar rahe hain.
        # Ye code counter maintain karta hai,
        # actual LLM call hona zaroori nahi.
    }


# ============================================================
# 13. ITINERARY AGENT
# ============================================================

def itinerary_agent(state: TravelState):
    # Ye agent flights aur hotels ke basis par itinerary banayega.


    prompt = f"""
Create a complete travel itinerary.

User Query:
{state['user_query']}

Flight Results:
{state['flight_results']}

Hotel Results:
{state['hotel_results']}

Make the itinerary practical, budget-aware, and easy to follow.
"""
    # LLM ke liye detailed prompt create kar rahe hain.
    #
    # f-string ki help se state ke actual values prompt mein insert hongi.
    #
    # Is prompt mein:
    # 1. User ki query
    # 2. Flight results
    # 3. Hotel results
    # 4. Itinerary banane ki instructions
    # sab include hain.


    response = llm.invoke([
        SystemMessage(content="You are an expert travel planner."),
        HumanMessage(content=prompt)
    ])
    # LLM ko 2 messages bhej rahe hain.
    #
    # SystemMessage:
    # LLM ko role de rahe hain: expert travel planner.
    #
    # HumanMessage:
    # Actual travel planning prompt.
    #
    # invoke():
    # LLM ko request bhejta hai aur response return karta hai.


    return {
        "itinerary": response.content,
        # LLM ka text response state mein itinerary ke andar save kar rahe hain.
        #
        # response:
        # LLM ka complete response object.
        #
        # response.content:
        # Sirf generated text.


        "messages": [response],
        # LLM ka complete response message history mein add kar rahe hain.
        # Isse conversation state mein AI response store hoga.


        "llm_calls": state.get("llm_calls", 0) + 1
        # Counter ko 1 se increment kar rahe hain.
    }


# ============================================================
# 14. FINAL RESPONSE AGENT
# ============================================================

def final_agent(state: TravelState):
    # Ye graph ka final AI response generate karega.
    # Flights, hotels aur itinerary ko combine karke
    # user ko formatted travel response dega.


    final_prompt = f"""
Generate the final travel response for the user.

User Request:
{state['user_query']}

Flights:
{state['flight_results']}

Hotels:
{state['hotel_results']}

Itinerary:
{state['itinerary']}

Format the final answer beautifully using these sections:

1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Day-by-Day Itinerary
5. Estimated Budget
6. Final Recommendations

Important:
- Be clear and practical.
- Mention that live flight API may not provide ticket prices if pricing is unavailable.
- Keep the response useful for real travel planning.
"""
    # Final response ke liye prompt bana rahe hain.
    #
    # Is prompt mein previous agents ke results pass kar rahe hain.
    #
    # LLM ko output ke 6 sections mein response generate karne ke liye bol rahe hain.


    response = llm.invoke([
        SystemMessage(
            content="You are a professional AI travel booking assistant."
        ),
        HumanMessage(content=final_prompt)
    ])
    # Final LLM call.
    #
    # SystemMessage:
    # AI ka role define karta hai.
    #
    # HumanMessage:
    # Final answer ke liye instructions aur data provide karta hai.


    return {
        "messages": [response],
        # Final LLM response ko messages list mein add kar rahe hain.


        "llm_calls": state.get("llm_calls", 0) + 1
        # Counter ko 1 se increment kar rahe hain.
    }


# ============================================================
# 15. BUILD THE GRAPH
# ============================================================

graph = StateGraph(TravelState)
# TravelState ke basis par StateGraph object create kar rahe hain.
# Ye graph ka container hai jisme nodes aur edges add karenge.


graph.add_node("flight_agent", flight_agent)
# Graph mein flight_agent node register kar rahe hain.
# Node name: "flight_agent"
# Function: flight_agent


graph.add_node("hotel_agent", hotel_agent)
# Hotel agent ko graph mein register kar rahe hain.


graph.add_node("itinerary_agent", itinerary_agent)
# Itinerary agent ko graph mein register kar rahe hain.


graph.add_node("final_agent", final_agent)
# Final response agent ko graph mein register kar rahe hain.


# ============================================================
# 16. GRAPH EDGES / EXECUTION FLOW
# ============================================================

graph.add_edge(START, "flight_agent")
# Graph START hone ke baad flight_agent run hoga.


graph.add_edge("flight_agent", "hotel_agent")
# Flight agent complete hone ke baad hotel_agent run hoga.


graph.add_edge("hotel_agent", "itinerary_agent")
# Hotel agent complete hone ke baad itinerary_agent run hoga.


graph.add_edge("itinerary_agent", "final_agent")
# Itinerary agent complete hone ke baad final_agent run hoga.


graph.add_edge("final_agent", END)
# Final agent complete hone ke baad graph END ho jayega.


# Complete execution flow:
#
# START
#   |
#   v
# Flight Agent
#   |
#   v
# Hotel Agent
#   |
#   v
# Itinerary Agent
#   |
#   v
# Final Agent
#   |
#   v
# END


# ============================================================
# 17. POSTGRESQL CHECKPOINTER
# ============================================================

DATABASE_URL = get_database_url()
# Function call karke database URL read kar rahe hain.
# Agar SSL mode missing hai toh function add karega.


_conn = psycopg.connect(
    DATABASE_URL,
    autocommit=True,
    row_factory=dict_row
)
# PostgreSQL database se connection establish kar rahe hain.
#
# DATABASE_URL:
# PostgreSQL database ka connection URL.
#
# autocommit=True:
# Transactions ko automatically commit karne ki setting.
#
# row_factory=dict_row:
# Database rows ko dictionary-like format mein fetch karne ke liye.


checkpointer = PostgresSaver(_conn)
# PostgreSQL connection ko PostgresSaver ke saath connect kar rahe hain.
# Ye graph checkpoints save/load karne mein help karega.


checkpointer.setup()
# Checkpointer ke required database tables/schema ko initialize karta hai.
# Isse pehle required database setup complete ho sakta hai.


travel_graph = graph.compile(checkpointer=checkpointer)
# Graph ko compile karke executable graph bana rahe hain.
#
# checkpointer:
# Graph execution ke checkpoints PostgreSQL mein save honge.
#
# Ab travel_graph.invoke() ke through graph run kar sakte hain.


# ============================================================
# 18. FUNCTION FOR FASTAPI
# ============================================================

def run_travel_agent(
    user_input: str,
    thread_id: str | None = None
):
    # FastAPI se is function ko call kiya ja sakta hai.
    #
    # user_input:
    # User ka travel question.
    #
    # thread_id:
    # Conversation ko identify karne ke liye optional ID.
    #
    # str | None:
    # Value string ho sakti hai ya None.


    if not thread_id:
        # Agar thread_id provide nahi hui hai,
        # toh ek unique thread ID generate karenge.


        thread_id = f"user_{uuid.uuid4().hex}"
        # uuid4() random unique UUID generate karta hai.
        # .hex usko hexadecimal string format mein convert karta hai.
        #
        # Example:
        # user_a1b2c3d4...


    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    # Graph ko configuration pass kar rahe hain.
    #
    # thread_id:
    # Checkpointer ko batata hai ki kis conversation/thread
    # ka checkpoint use karna hai.
    #
    # Same thread_id use karne par
    # checkpoints ko same conversation se associate kiya ja sakta hai.


    result = travel_graph.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            # User ke input ko HumanMessage mein convert kar rahe hain.
            # Messages list ka first message user ka question hai.


            "user_query": user_input,
            # Original user query state mein store kar rahe hain.


            "flight_results": "",
            # Starting mein flight results empty hain.


            "hotel_results": "",
            # Starting mein hotel results empty hain.


            "itinerary": "",
            # Starting mein itinerary empty hai.


            "llm_calls": 0
            # LLM/tool-related counter ko 0 se start kar rahe hain.
        },
        config=config
    )
    # Graph execution start kar rahe hain.
    #
    # invoke():
    # Graph ko given initial state ke saath run karta hai.
    #
    # config:
    # Thread ID provide karta hai jisse checkpointer
    # conversation checkpoints associate kar sake.
    #
    # Result mein final state return hoti hai.


    final_answer = result["messages"][-1].content
    # Messages list ka last message nikal rahe hain.
    #
    # [-1]:
    # List ka last element.
    #
    # .content:
    # AI ke response ka actual text.
    #
    # Kyunki final_agent last mein run hota hai,
    # yahan normally final AI response milega.


    return {
        "thread_id": thread_id,
        # Conversation ki ID return kar rahe hain.
        # Frontend future requests mein ise use kar sakta hai.


        "answer": final_answer,
        # Final AI-generated answer return kar rahe hain.


        "flight_results": result.get("flight_results", ""),
        # Final state se flight results nikal rahe hain.
        # Agar key missing ho toh empty string return hogi.


        "hotel_results": result.get("hotel_results", ""),
        # Final state se hotel results nikal rahe hain.


        "itinerary": result.get("itinerary", ""),
        # Final state se generated itinerary nikal rahe hain.


        "llm_calls": result.get("llm_calls", 0),
        # Total counter value return kar rahe hain.
        # Key missing hone par 0 return hoga.
    }