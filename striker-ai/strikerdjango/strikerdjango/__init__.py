from django.http import JsonResponse
import os
import openai
from dotenv import load_dotenv, find_dotenv
from crewai import Agent
from crewai import Crew
from crewai import Process
from crewai import Task
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_openai import ChatOpenAI

def crewai_endpoint(request):
    playerInfo = request.GET.get('playerInfo', "this is an invalid response")

    default_llm = ChatOpenAI(
    openai_api_base="http://localhost:1234/v1",
    openai_api_key="not-needed",
    model_name="TheBloke",
    )

    '''p
    arams = {
        "engine": "google",
        "gl": "us",
        "hl": "en",
    }
    search_tool = SerpAPIWrapper(params=params)
    '''
    search_tool = DuckDuckGoSearchRun()


    # Search query modifier agent with custom tools and delegation capability
    searcher_eval = Agent(
    role='Edward, Expert Search Query Consultor',
    goal=f'Please evaluate current search results and modify the search query to improve the results for {playerInfo}.',
    verbose=True,
    memory=True,
    backstory="You are an expert in refining search queries for sports topics. You have been asked to modify and make prompts better anytime a search is executed. You get tippepd for every informative, relevant, and effective search query that you generate.",
    tools=[search_tool],
    allow_delegation=True,
    llm=default_llm
    )

    # Expert searcher based upon the given playerInfo. 
    searcher_gen = Agent(
    role='Sam, Expert Searcher',
    goal=f'Find sports information online relevent to this specific player: {playerInfo}', 
    verbose=True,
    memory=True,
    backstory="You are an expert in searching for specific information and statistics for particular sports players. You have been in this industry for 25 years and you recieve a tip for every relevant, informative, or interesting fact you find about a specific sports player",
    tools=[search_tool],
    allow_delegation=True,
    llm=default_llm
    )

    # Resarch task
    research_task = Task(
    description=f"""Gather and research information onlne about this specific sports player: {playerInfo} """,
    expected_output='A specific curation of high quality statistics and information about the player. Your response should be quantative-results focused and include all possible statistics that exist about the player online, including from specific games, seasons, teams, and live data from the player. The paragraph can be quite long, but should include at least 30 different quantative stats about the player online.',
    tools=[search_tool],
    agent=searcher_gen,
    )

    output_analyzer = Agent(
    role='Adam, Expert Analyzer',
    goal=f'Look at the data given to you in the context from the research_task and using your given tools develop a player report is based on the given information, and this should be relatively brief and include all raw stats.', 
    verbose=True,
    memory=True,
    backstory="You are an expert in taking in data and statistics and turning them into graphs. You have been in this industry for 25 years and you recieve a tip for every relevant, informative, or interesting graph you create.",
    tools=[],
    allow_delegation=True,
    llm=default_llm
    )

    output_validator = Agent(
    role='Vlad, Expert Validator',
    goal=f'take the information given to you and turn it into a json acceptable format and it should include all aspects of the comprehensive quanttative report.', 
    verbose=True,
    memory=True,
    backstory="You are an expert in getting information given to you and turn it into a json. You have been in this industry for 25 years and you recieve a tip for every relevant, informative, or interesting fact you find about a specific sports player",
    tools=[],
    allow_delegation=True,
    llm=default_llm
    )
    # Writing task with language model configuration
    output_validation = Task(
    description=f"""Generate a json output filled with all included stats and player information, 
    given the context from the research_task Task about {playerInfo}.
    """,
    expected_output='You output JSON that includes all of the quantitative information about the player from the given research_task. You also preform analysis on the information and automatically generate graphs and trend insights based upon this data, and use your agents to preform analysis, and validate the output to be turned into a json output.',
    # two agents: 1st analyze the data 
        # 2nd validate the output and turn into json based on analyis (and including raw data)
    tools=[],
    agent=output_analyzer,
    context=[research_task],
    async_execution=False,
    output_file='eval_timestamp.json'  # Example of output customization
    )
    # Forming the tech-focused crew with enhanced configurations
    crew = Crew(
    agents=[searcher_gen, searcher_eval, output_analyzer, output_validator],
    tasks=[research_task, output_validation],
    manager_llm=default_llm,
    # later return back to this and change again to be sure that the modoel is the best
    process=Process.sequential,
    )

    return JsonResponse({'response': crew.kickoff()})