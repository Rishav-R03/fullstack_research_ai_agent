from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from datetime import datetime

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="search the web"
)

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=100)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

def save_to_txt(data: str, filename: str = 'research_output.txt'):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = f"--- Research Output --- \nTimestamp: {timestamp} \n\n{data}\n\n"

    with open(filename, 'a', encoding='utf-8') as file:
        file.write(formatted_text) # Corrected: Changed f.write to file.write

    return f"Data successfully saved to {filename}"

save_tool = Tool(
    name="save_txt",
    func=save_to_txt,
    description="saves research data into a text file."
)