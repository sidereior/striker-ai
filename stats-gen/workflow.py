import os
os.environ["OPENAI_API_KEY"] = "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"

from crewai import Agent
from crewai import Crew
from crewai import Process
from langchain_community.tools import DuckDuckGoSearchRun
search_tool = DuckDuckGoSearchRun()

# Topic for the crew run
topic = 'Inter Milan'

# Creating a senior researcher agent with memory and verbose mode
researcher = Agent(
  role='Senior Researcher',
  goal=f'Research why {topic} are so good this season',
  verbose=True,
  memory=True,
  backstory="",
  tools=[search_tool],
  allow_delegation=True
)

# Creating a writer agent with custom tools and delegation capability
writer = Agent(
  role='Writer',
  goal=f'Narrate compelling stories about {topic} this season',
  verbose=True,
  memory=True,
  backstory="",
  tools=[search_tool],
  allow_delegation=False
)
from crewai import Task

# Research task
research_task = Task(
  description=f"""Identify the reasons {topic} are so successful this season.""",
  expected_output='A comprehensive 3 paragraphs long report on the latest AI trends.',
  tools=[search_tool],
  agent=researcher,
)

# Writing task with language model configuration
write_task = Task(
  description=f"""Compose an insightful article on {topic}.
  Focus on the latest trends and their impacting the sport.
  This article should be easy to understand, engaging, and positive.""",
  expected_output=f'A 4 paragraph article on {topic}.',
  tools=[search_tool],
  agent=writer,
  async_execution=False,
  output_file='new-blog-post.md'  # Example of output customization
)
# Forming the tech-focused crew with enhanced configurations
crew = Crew(
  agents=[researcher, writer],
  tasks=[research_task, write_task],
  process=Process.sequential  # Optional: Sequential task execution is default
)
# Starting the task execution process with enhanced feedback
result = crew.kickoff()
print(result)