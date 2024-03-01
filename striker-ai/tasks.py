from crewai import Task

# Sample JSON input for keyword extraction
input_json = {
    "player": {
        "firstName": "Christian",
        "lastName": "Pulišić",
        "bio": {
            "citizenship": "US"
        }
    }
}

# Tasks for each step
keyword_extraction_task = Task(
    description="Extract keywords from input JSON",
    agent=input_agent,
    extra_content=input_json  # Pass the JSON input here
)

search_info_task = Task(
    description="Find detailed player info",
    agent=searcher_finder_agent
)

analyze_info_task = Task(
    description="Analyze the found player info",
    agent=searcher_analyzer_agent
)

adapt_search_task = Task(
    description="Adapt search terms based on analysis",
    agent=searcher_adapter_agent
)
