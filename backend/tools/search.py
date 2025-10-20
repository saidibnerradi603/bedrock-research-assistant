from langchain_core.tools import tool
from tavily import TavilyClient
from perplexity import Perplexity
from config.settings import get_settings


settings = get_settings()

tavily_client = TavilyClient(api_key=settings.tavily_api_key)
perplexity_client = Perplexity(api_key=settings.perplexity_api_key)




@tool
def tavily_search(query: str) -> str:
    """
    Search the web using Tavily API for comprehensive research results.
    
    Args:
        query: The search query string
        
    Returns:
        Formatted search results with titles, URLs, and content snippets
    """
    if not tavily_client:
        return "Error: Tavily client not initialized. Please check your API key."
    
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",  # More comprehensive search
            max_results=5,           # Balanced number of results
            include_answer=True,     # Include AI-generated answer
            include_raw_content=False # Focus on summaries
        )
        
        formatted_results = []
        
        if response.get('answer'):
            formatted_results.append(f"**AI Summary:** {response['answer']}\n")
        
        if response.get('results'):
            formatted_results.append("**Search Results:**")
            for i, result in enumerate(response['results'], 1):
                title = result.get('title', 'No title')
                url = result.get('url', 'No URL')
                content = result.get('content', 'No content available')
                
                formatted_results.append(
                    f"\n{i}. **{title}**\n"
                    f"   URL: {url}\n"
                    f"   Summary: {content}"
                )
        
        return "\n".join(formatted_results)
    
    except Exception as e:
        return f"Error performing search: {str(e)}"
    


@tool
def perplexity_search(query: str) -> str:
    """
    Search using Perplexity AI for intelligent web search with AI-powered summaries.
    
    Args:
        query: The search query string
        
    Returns:
        AI-generated summary with source citations
    """

    if not perplexity_client:
        return "Error: Perplexity client not initialized. Please check your API key or package installation."
    
    try:
        try:
            search = perplexity_client.search(query=query, max_results=5)
            results = search.get('results', [])
        except AttributeError:
            search = perplexity_client.search.create(
                query=query,
                max_results=5,             
            )
            results = search.results if hasattr(search, 'results') else []
        
        formatted_results = []
        formatted_results.append(f"**Perplexity Search Results for:** {query}\n")
        
        if results:
            for i, result in enumerate(results, 1):
                if hasattr(result, 'title'):
                    title = result.title
                    url = getattr(result, 'url', 'No URL')
                    snippet = getattr(result, 'snippet', getattr(result, 'content', 'No content available'))
                elif isinstance(result, dict):
                    title = result.get('title', 'No title')
                    url = result.get('url', 'No URL')
                    snippet = result.get('snippet', result.get('content', 'No content available'))
                else:
                    title = str(result)[:100]
                    url = 'No URL'
                    snippet = 'No content available'
                
                formatted_results.append(
                    f"\n{i}. **{title}**\n"
                    f"   URL: {url}\n"
                    f"   Summary: {snippet}"
                )
        else:
            formatted_results.append("No results found.")
        
        return "\n".join(formatted_results)
    
    except Exception as e:
        return f"Error performing Perplexity search: {str(e)}. Falling back to Tavily search."
    
    
