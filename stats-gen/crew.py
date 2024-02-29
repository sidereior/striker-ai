from crewai import Crew, Process

# Assemble the crew
crew = Crew(
    agents=[input_agent, searcher_finder_agent, searcher_analyzer_agent, searcher_adapter_agent],
    tasks=[keyword_extraction_task, search_info_task, analyze_info_task, adapt_search_task],
    manager_llm=ChatOpenAI(temperature=0, model="gpt-4"),
    process=Process.heirarchical,
    verbose=2
)

# Execute the crew process
result = crew.kickoff()
print("Crew execution result:", result)
