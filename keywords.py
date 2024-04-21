import networkx as nx
import json
from llm import callGPT


def create_graph(keywords: dict, directed: bool = False) -> nx.Graph:
    """
    Create a graph from the keywords dictionary. Each keyword is a node. If the description of one keyword
    contains another keyword, an edge is created between them.

    Args:
    keywords (dict): Dictionary with keywords and their descriptions.
    directed (bool): Determines if the resulting graph should be directed. False means the graph is undirected.

    Returns:
    nx.Graph: The resulting graph, which could be either directed or undirected.
    """
    graph = nx.DiGraph() if directed else nx.Graph()
    keywords_lower = {k.lower(): v.lower() for k, v in keywords.items()}  # Work with lowercase to ensure case insensitivity

    # Add nodes with the actual keyword (not lowercased) for better output handling
    for key in keywords:
        graph.add_node(key)  

    # Add edges based on case insensitive comparison
    for key, description in keywords_lower.items():
        for potential_key in keywords_lower:
            if potential_key in description and key != potential_key:
                graph.add_edge(key, potential_key)  # Use original keys for the nodes

    return graph

def spot_keywords(text: str, keywords: dict, depth: int = 1, graph=None) -> set:
    """
    Extended version of spot_keywords that considers graph relations among keywords to identify related terms.

    Args:
    text (str): The text to search within.
    keywords (dict): A dictionary where the keys are terms to search for.
    depth (int): The depth to traverse in the keyword graph. depth=1 means only direct appearances.
    graph (nx.Graph): A graph representing relationships between keywords.

    Returns:
    set: A set of keys that were found directly in the text and their related keys up to the specified depth.
    """
    if depth >= 2 and graph is None:
        raise ValueError("A graph must be provided for depth >= 2")

    found_keys = set()
    text_lower = text.lower()

    # Identify direct appearances
    for key in keywords.keys():
        if key.lower() in text_lower:
            found_keys.add(key)

    # Use the graph to find related keywords based on the depth
    if depth >= 2:
        related_keys = set(found_keys)
        for _ in range(depth - 1):
            new_related = set()
            for key in related_keys:
                # Use neighbors from graph directly
                new_related.update(graph.neighbors(key))
            related_keys.update(new_related)
        found_keys.update(related_keys)

    return found_keys


def extract_keywords(current_keywords: dict, text: str) -> dict:
    """
    Leverages an external GPT model to analyze a text and update the current keywords dictionary based on GPT's response.
    
    Args:
    current_keywords (dict): The current dictionary containing keywords and their descriptions.
    text (str): The text from which to extract and update keywords.
    
    Returns:
    dict: An updated dictionary with new or modified keywords.
    """
    # Handle empty current_keywords dictionary by providing a default placeholder
    if not current_keywords:
        current_keywords = {"placeholder": "The placeholder appears as keyword when no existing keyword detected in the given text."}

    # Define the prompt for the AI with a clear specification about the response format
    prompt = f"""
    You are a keyword updater, only responsible for the keyword-updating step in a more complex text-game system. Below is the current keyword dictionary's content:
    
    {"{"}{", ".join([f'"{key}": "{value}"' for key, value in current_keywords.items()])}{'}'}
    
    ---

    Text:
    {text}

    ---

    Your response should be strictly formatted as a Python dictionary in valid JSON format, nothing more, nothing else. This format is necessary because your response will be parsed directly by the program. Only include those keywords that you want to *add* as new keywords or existing keywords that you want to *update its explanation*. Keep in mind: keywords are used only for important note-taking and information storage. For example, the explanation of the keyword "letter form father" should contain the direct  content of the letter. The keywords chosen should be those that are *specific to the story* - not general keywords! 

    Now, give the updated keyword dictionary based on the given text:
    """
    
    # Use the existing callGPT function to send the prompt and get the AI's response
    try:
        ai_response = callGPT([{'role': 'system', 'content': prompt}])
        # Use json.loads for safer parsing of the response into a dictionary
        updated_keywords = json.loads(ai_response)
        return updated_keywords
    except json.JSONDecodeError:
        print("Parsing error: The response was not valid JSON.")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


if __name__ == "__main__":
    if True:
        # Example text to analyze
        example_text = "As the autumn leaves began to fall, the ancient town of Eldershire seemed to whisper secrets of bygone eras."
        # Initially empty keywords dictionary
        example_keywords = {}

        # Run the extract_keywords function with the example inputs
        result = extract_keywords(example_keywords, example_text)
        print("Extracted Keywords:", result)
    else:
        # Define the keywords dictionary
        keywords = {
            "Eldershire": "A town with ancient secrets and whispers of bygone eras.",
            "Whitmore estate": "An old, abandoned mansion in Eldershire once vibrant but now cloaked in mystery.",
            "ballroom": "A once-lavish room in the Whitmore estate, now overtaken by shadows and dust.",
            "chandelier": "A grand but tarnished and unlit fixture in the ballroom of the Whitmore estate.",
            "figure": "A lone, cloaked individual wandering through the halls of the Whitmore estate."
        }

        # Text to analyze
        text = "You have arrived ballroom."

        # Create the graph with case handling fixed
        keyword_graph = create_graph(keywords, directed=False)

        # Perform the depth 2 keyword spotting
        found_keywords = spot_keywords(text, keywords, depth=2, graph=keyword_graph)
        print(found_keywords)
