from crewai import Agent

# Input Agent
input_agent = Agent(
    role='Input Processor',
    goal='Extract search keywords from JSON input',
    tools=[Tool(name="JSON Keyword Extractor", func=extract_keywords)],
    verbose=True
)

# Searcher-Finder Agent
searcher_finder_agent = Agent(
    role='Searcher-Finder',
    goal='Find detailed information and statistics about the player',
    tools=[Tool(name="Player Info Searcher", func=search_player_info)],
    allow_delegation=True,
    verbose=True
)

# Searcher-Analyzer Agent
searcher_analyzer_agent = Agent(
    role='Searcher-Analyzer',
    goal='Analyze information and extract detailed statistics',
    tools=[Tool(name="Player Stats Analyzer", func=analyze_player_stats)],
    allow_delegation=True,
    verbose=True
)

# Searcher-Adapter Agent
searcher_adapter_agent = Agent(
    role='Searcher-Adapter',
    goal='Adapt search strategies based on missing or inaccurate stats',
    tools=[Tool(name="Search Term Modifier", func=modify_search_terms)],
    allow_delegation=True,
    verbose=True
)
