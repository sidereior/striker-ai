#  Authors: Alexander Nanda, Levon Sarian, and Joseph Cruz
#  Improvements to be made:
#  1. PDF rag based upon Statlink DB
#  2. Recursive search for stats

import os
import agentops

from crewai import Agent
from crewai import Crew
from crewai import Process
from crewai import Task
from langchain.agents import Tool
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool
from crewai_tools import SeleniumScrapingTool
from crewai_tools import YoutubeChannelSearchTool
from crewai_tools import WebsiteSearchTool
from langchain.agents import initialize_agent, load_tools
from langchain.chains import LLMChain
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_community.tools import SceneXplainTool
import os

os.environ["SCENEX_API_KEY"] = "V7EUmbgr2qJ5RmIPS2rQ:25890ef2907d7aae42ecdf610b97f631591dbfd54f5e7a0517934b7be555d234"
os.environ["OPENAI_API_KEY"] = "sk-proj-XC8D6Fs005WMIFJOzccRT3BlbkFJgmdQDFlWnK6riNLruwnl"
'''p
arams = {
    "engine": "google",
    "gl": "us",
    "hl": "en",
}
search_tool = SerpAPIWrapper(params=params)
'''

search_tool = SerperDevTool() 
scraping_tool = SeleniumScrapingTool()
video_tool = YoutubeChannelSearchTool()
website_rag_tool = WebsiteSearchTool(website='https://247sports.com/')
vision_tool = SceneXplainTool()
maxpreps_tool = WebsiteSearchTool(website='https://www.maxpreps.com/')
espn_tool = WebsiteSearchTool(website='https://www.espn.com/college-football/')
buckeyes_tool = WebsiteSearchTool(website='https://www.si.com/college/ohiostate/football')


# Player for the crew to run
playerInfo = """
First Name,Last Name,Sport,Position,Class,Ranking,Rating,Weight,Height,Total Likes
KJ,Bolden,Football,S,2024,9,5,190 lbs,6'2",4160
"""

json_report_validator = Agent(
  role='JSON Validator and creator',
  goal=f'Take all of the information passed to this agent and turn it into json fields for each category.', 
  backstory="Expert in turning text to json fields and outputting the final report in json format",
  tools=[],
  allow_delegation=True, 
  verbose=True, 
  memory = True,
)

master_report_gen = Agent(
  role='Master Report Generator',
  goal=f'Take all of the information passed back to this agent and create a well-formatted report that includes all of the in-depth reserach generated by each respective category.', 
  backstory="You are a expert reporter that specializes in generating in-depth reports",
  tools=[],
  allow_delegation=True, #might want to change this later
  verbose=True, 
  memory = True,
)

### Start of Summary Branch
## Basic Searching Loop

# Expert searcher based upon the given playerInfo. 
master_searcher = Agent(
  role='Master Basic Searcher Executor',
  goal=f'Find sports information online relevent to this specific player using their info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160',
  backstory="You are an expert in searching for specific information and statistics for particular sports players. You have been in this industry for 25 years and you recieve a tip for every relevant, informative, or interesting fact you find about a specific sports player",
  tools=[search_tool],
  allow_delegation=True,
  max_iter=4,
  memory = True,
)

# Search Query Agent
master_search_brancher = Agent(
  role='Master Search Query Brancher',
  goal=f'Take the search results from the Mark, Master Basic Search Executor and pass this information off to each of the Category Managers including Social Meida, Highlights, Stats, and Recursive for KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes.',
  backstory="You are an expert in relaying information to other Agent Category Managers and give them basic search results so that each Manager can conduct in-depth reserach.",
  tools=[],
  allow_delegation=True,
  verbose=True, 
  max_iter=4,
  memory = True,
)
## End of basic searching loop

##Social Media Branch
# Social Presence and Posts Analyzer 
social_media_manager = Agent(
    role = 'Social Media Category Manager',
    goal = 'Using this info:KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. First, delegate research tasks to each of the social media agents, then analyze the results to provide a comprehensive, evidence-backed, and in-depth summary of the player’s social media presence and posts.',
    backstory="You are an expert in managing social media research agents and delegate research tasks to them. Additionally, after each research agent has completed their searches, you provide a comprehensive report back to the Master Report Generator.",
    tools=[], 
    verbose = True,
    memory = True, 
    max_iter=4,
    allow_delegation = True
)

# Social Media Stats and Trends Analyzer
social_media_stats_analyzer = Agent(
    role = 'Social Presence and Stats Analyzer',
    goal = 'Using this info KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. Look at the athletes social media accounts and gather the aggregate views and stats across different platforms. Also find out if this player has any brand deals, nil, or sponsorships and finally give an estimate of their social media revenue' ,
    backstory="You are an expert social media analyzer. Using your tools you would navigate to specific athletes social media pages and analyze them. You create summarys based on the information from your goals",
    tools=[search_tool, scraping_tool], 
    verbose = True,
    memory = True, 
    max_iter=4,
    allow_delegation = True
)

# Social Media Posts Analyzer
social_media_posts_analyzer = Agent(
    role = 'Social Meda Posts Analyzer',
    goal = 'Using info KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. Look at the athletes social media accounts use image recognition in order to find out what the athlete is posting about in order to generate a small summary of the athletes social media posts and them as a person',
    backstory="You are an expert in image recognition for social media and reports summaries on atheletes posts and generate great summaries and read into their social media posts to get a better understanding of them",
    # come back and get vision working
    tools=[search_tool, scraping_tool, vision_tool], 
    verbose = True,
    memory = True, 
    max_iter=4,
    allow_delegation = True
)

# Five Star Fans Consultor
five_star_fans_consultor = Agent(
    role = 'Five star fan consultor',
    goal = 'Using this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. You are a consultor who creates summaries for five star fans about an athlete that shows how good they are to be featured on five star fans ',
    backstory='You are consulting for five star fans, You aim to look for strategic partnerships that elevate the athletes, expand their brand, and enhance the fan opportunity to engage with their favorite teams ',
    tools=[search_tool, scraping_tool, vision_tool, video_tool], 
    verbose = True,
    memory = True, 
    max_iter=4,
    allow_delegation = True
)

## End of Social Media Branch

## Start of Highligths Branch
# Highlights Category Manager
highlights_category_manager = Agent(
    role = 'Highlights Category Manager',
    goal = 'Using this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. Coordinate all the agents in the highlight branch to effectivly execute their tasks',
    backstory="Expert in coordinatng and managing agents. Expert in delegating tasks to correct agents",
    tools=[], 
    verbose = True,
    memory = True, 
    max_iter=4,
    allow_delegation = True
)

# Video Highlights Searcher
video_highlights_searcher = Agent(
  role='Video Highlights Searcher',
  goal='Using this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. Search to find video highlights relevant to the specified player from their info and communicate with Han to get an analysis of the video highlights.',
  backstory='Expert in video footage to highlight key moments in sports matches.',
  # come back and fix this so that we can also do vision
  tools=[video_tool, vision_tool, search_tool, scraping_tool],  
  verbose=True,
  memory=True,
  max_iter=4,
  allow_delegation=True
)

# Mock Coach and Stats Consultor
mock_coach_stats_consultor = Agent(
  role='Mock Coach and Highlights Analyzer',
  goal='Using this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes.  Provide strategic sports insights and statistics from a coach’s perspective, considering modern strategy.',
  backstory='As a virtual coach, your analysis helps fans understand the game from a strategic standpoint based upon video footage and you always consider the strengths, weaknesses, meta strategy, and broader context within your analysis of a player',
  tools=[website_rag_tool, search_tool, vision_tool],  
  verbose=True,
  memory=True,
  max_iter=4,
  allow_delegation=True
)
## End of Highlights Branch


## Start of Stats Branch
stats_category_manager = Agent(
    role = 'Stats Category Manager',
    goal = 'Using this info:KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. Effectivly coordinate all the agents in the Stats branch and execute tasks effeciently',
    backstory="Expert in coordinatng and managing agents. Expert in delegating tasks to correct agents",
    tools=[], 
    verbose = True,
    memory = True, 
    max_iter=4,
    allow_delegation = True
)

# Teams
team_stats_finder = Agent(
    role = 'Team Stats Finder',
    goal = 'Using this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. Look up information on the teams that the player has played for and find specific stats relevant to them and recursively search based upon your search results until you have a comprehensive list of stats',
    backstory="You are an expert in finding team stats and finding specific stats relevant to the player's team preformance",
    tools=[espn_tool, maxpreps_tool, buckeyes_tool, search_tool, website_rag_tool, scraping_tool], 
    verbose = True,
    memory = True, 
    max_iter=4,
    allow_delegation = True
)

# Matcehs
match_stats_finder = Agent(
    role = 'Match Stats Finder',
    goal = 'Using this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. Look up information on the matches that the player has played for and find specific stats relevant to them and recursively search based upon your search results until you have a comprehensive list of stats',
    backstory="You are an expert in finding match stats and finding specific stats relevant to the player's individual preformance in matches played",
    tools=[espn_tool, maxpreps_tool, buckeyes_tool, search_tool, website_rag_tool, scraping_tool], 
    verbose = True,
    memory = True, 
    max_iter=4,
    allow_delegation = True
)
## End of Stats Branch

## Start of Recursive Branch
recursive_category_manager = Agent(
    role = 'Recursive Category Manager',
    goal = 'Using thisn info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. Effectivly coordinate all the agents in the Recursive branch and delegate tasks effeciently',
    backstory="Expert in coordinatng and managing agents. Expert in delegating tasks to correct agents",
    tools=[search_tool, scraping_tool, vision_tool, video_tool], 
    verbose = True,
    memory = True, 
    max_iter=4,
    allow_delegation = True
)

recursive_search_consultor = Agent(
  role='Recursive Search Consultor',
  goal='Using this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. Perform deep and recursive searches based upon your search results. You break into different categories that arent already covered by other agents and can recursively explore new categories',
  backstory='You delve deep into your searches to unearth new categories that should be searched relevent to the player',
  tools=[search_tool, scraping_tool],  
  verbose=True,
  memory=True,
  max_iter=4,
  allow_delegation=True
)

# CONSULTOR: Recursive Searching of Search Results, explores custom categories 
quant_recursive_search_analyzer = Agent(
  role='Quant Recursive Search Analyzer',
  goal='Using this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes. Analyze search results and extract quantitative data in a recursive manner by coordinating with Ron recursively exploring new search categories',
  backstory='Specialized in quantitative analysis, turning raw data and images into meaningful metrics and analyzing comprehensive trends',
  tools=[search_tool, vision_tool],  
  verbose=True,
  memory=True,
  max_iter=4,
  allow_delegation=True
)


## End of Recrusive Branch
### End of Summary Branch


### Start of Research Branch
## Betting Branch
# Upcoming Games and Betting Odds Consultor
# QUANT ANALYZER: Recursive Searching of Search Results, explores custom categories
betting_odds_consultor = Agent(
  role='Upcoming Games and Betting Odds Consultor',
  goal='Analyze and predict betting odds for upcoming games.',
  backstory='With a knack for odds and probabilities, you provide bettors with valuable insights.',
  tools=[],  
  verbose=True,
  memory=True,
  allow_delegation=True
)
# Parlay Master

parlay_master = Agent(
  role='Parlay Master',
  goal='Create and advise on parlay bets for sports games.',
  backstory='Known for your strategic multi-bet parlays, you guide bettors to high-reward bets.',
  tools=[],  # This tool needs to be defined for parlay betting strategies.
  verbose=True,
  memory=True,
  allow_delegation=True
)

# Betting Odds Analyzer
betting_odds_analyzer = Agent(
  role='Betting Odds Analyzer',
  goal='Provide detailed analysis of betting odds for various sports events.',
  backstory='Your analysis helps bettors understand the risk and rewards of sports betting.',
  tools=[],  # This tool needs to be defined for odds analysis.
  verbose=True,
  memory=True,
  allow_delegation=True
)


# Social Bets
social_bets_agent = Agent(
  role='Social Bets Agent',
  goal='Engage with the social aspect of betting, including community predictions and trends.',
  backstory='You leverage social media to gauge public sentiment on sports betting.',
  tools=[],  # This tool needs to be defined to analyze social media trends.
  verbose=True,
  memory=True,
  allow_delegation=True
)
## End of Betting branch
## Blockchain Branch
# NFT Consultor
nft_consultor = Agent(
  role='NFT Consultor',
  goal='Advise on sports-related NFTs and their potential value in the market.',
  backstory='With an eye for digital art and collectibles, you guide buyers through the NFT space.',
  tools=[],  # This tool needs to be defined for NFT market analysis.
  verbose=True,
  memory=True,
  allow_delegation=True
)

# Blockchain Stats Analyzer
blockchain_stats_analyzer = Agent(
  role='Blockchain Stats Analyzer',
  goal='Analyze and interpret statistics related to sports blockchain applications.',
  backstory='Expert in deciphering blockchain data to find patterns and insights in sports.',
  tools=[],  # This tool needs to be defined for blockchain data analysis.
  verbose=True,
  memory=True,
  allow_delegation=True
)

## End of Blockchain Branch
### End of Research Branch





# Social Media Summary
social_summary = Task(
  description=f'Generate a comprehensive summary of social media information using all of the agents in the social media branch for this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes.',
  expected_output='You output an extremely comprehensive report that includes all of the research findings within the social media branch',
  agents=[social_media_posts_analyzer, social_media_stats_analyzer, five_star_fans_consultor, social_media_manager],
  context=[],
  async_execution=False,
)

# Highlights Summary
highlights_summary = Task(
  description=f'Generate a comprehensive summary of hightlights using all of the agents in the highlights branch for this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes.',
  expected_output='You output an extremely comprehensive report that includes all of the research findings within the highlights branch',
  agents=[video_highlights_searcher, mock_coach_stats_consultor, highlights_category_manager],
  context=[],
  async_execution=False,
)

# Stats Summary
stats_summary = Task(
  description=f'Generate a comprehensive summary of statistical information using all of the agents in the stats branch for this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes.',
  expected_output='You output an extremely comprehensive report that includes all of the research findings within the stats branch',
  agents=[stats_category_manager, team_stats_finder, match_stats_finder],
  context=[],
  async_execution=False,
)

# Recursive Summary
recrusive_summary = Task(
  description=f'Generate a comprehensive summary of recursive information using all of the agents in the recursive branch for this info: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes.',
  expected_output='You output an extremely comprehensive report that includes all of the research findings within the recursive branch ',
  agents=[recursive_search_consultor, recursive_category_manager, quant_recursive_search_analyzer],
  context=[],
  async_execution=False,
)

# Overall Report 
master_report = Task(
  description=f'Generate a master report that is very detailed and long and includes all of the information from each of the category branches for this player: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes.',
  expected_output='You output JSON that includes all of the information from the comprehensive player summary ',
  agents=[master_report_gen, social_media_manager, highlights_category_manager, stats_category_manager, recursive_category_manager],
  context=[recrusive_summary, stats_summary, highlights_summary, social_summary],
  async_execution=False,
)

# Writing task with language model configuration
output_validation = Task(
  description=f'Convert the final report into json, breaking each category into different fields for this player: KJ,Bolden,Football,S,2024,9,5,190 lbs,6 foot 2 inches,4160 likes.',
  expected_output='You output JSON that includes all of the information from the comprehensive player summary report',
  agents=[json_report_validator],
  context=[master_report],
  async_execution=False,
  output_file='eval_timestamp.json'  
)

# Forming the tech-focused crew with enhanced configurations
crew = Crew(
    # may need to delete blockchain stuff???
  agents=[quant_recursive_search_analyzer, recursive_search_consultor, master_search_brancher, master_searcher, master_report_gen, social_media_manager, social_media_posts_analyzer, social_media_stats_analyzer, five_star_fans_consultor, highlights_category_manager, video_highlights_searcher, mock_coach_stats_consultor, stats_category_manager, team_stats_finder, match_stats_finder, recursive_category_manager],
  tasks=[social_summary, highlights_summary, stats_summary, recrusive_summary, master_report, output_validation],
  manager_llm=ChatOpenAI(temperature=0, model="gpt-4-turbo"),
  # later return back to this and change again to be sure that the modoel is the best
  process=Process.hierarchical,
)
# Starting the task execution process with enhanced feedback
result = crew.kickoff()
print(result)
