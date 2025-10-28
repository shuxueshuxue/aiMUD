import requests
import json

'''
available models:
anthropic/claude-sonnet-4.5
google/gemini-2.5-pro
(configured in config.json)
'''


def callGPT(messages: list, model: str = 'anthropic/claude-sonnet-4.5') -> str:
    print(f"GPT called. model:{model}, message_length = {len(str(messages))}")
    print("---------------------------------")
    print(messages)
    print("---------------------------------")
    # URL of the AI endpoint

    with open('config.json', 'r') as f:
        config = json.load(f)
    url = config['api_endpoint']
    api_key = config.get('api_key', '')

    # Define the headers for the HTTP request
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    
    # Prepare the JSON body for the POST request
    body = {
        'model': model,
        'messages': messages,
        'max_tokens': 4000
    }
    
    # Try to send the POST request
    try:
        print(f"Sending request to: {url}")
        print(f"Headers: {headers}")
        print(f"Body: {json.dumps(body, indent=2)}")

        response = requests.post(url, headers=headers, json=body)

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text[:500]}")  # Print first 500 chars

        response.raise_for_status()  # Raises an HTTPError for bad responses
        # Parse the response JSON
        data = response.json()

        # This API uses OpenAI format for all models
        ai_response = data['choices'][0]['message']['content']

        return ai_response
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        return f"An error occurred: {str(e)}"
    except KeyError as e:
        print(f"Parsing error: {str(e)}")
        print(f"Response data: {data}")
        return f"Failed to extract AI's response: {str(e)}"

def continueStory(progress: str, general_styles: str, player: str, player_input: str, keywords: dict, model: str = 'anthropic/claude-sonnet-4.5') -> str:
    # Create a rich contextual narrative with explicit instructions for the AI
    context = f"{general_styles} In the latest part of the story, {progress} The main character, {player}, "
    context += f"now decides to: {player_input}. This is a game setting; focus on detailed, cinematic descriptions. "
    context += "Keep the response concise, aiming for 1 or 2 paragraphs only."
    
    # Append supplementary context from keywords
    supplementary_context = " Relevant notes: " + ", ".join(f"{k}: {v}" for k, v in keywords.items())
    
    # Generate the list of messages for the AI, including the detailed instructions
    messages = [
        {'role': 'user', 'content': context + supplementary_context}
    ]
    
    # Call the callGPT function with the generated messages
    return callGPT(messages, model)

# Example usage
if __name__ == "__main__":
    # Example story inputs
    progress = "the hero has just discovered a hidden map"
    general_styles = "A mystical and adventurous tone"
    player = "Eldric the Brave"
    player_input = "decides to explore the dark forest alone"
    keywords = {
        "ancient artifact": "a powerful relic of untold power",
        "dark forest": "a mysterious and foreboding place filled with unknown dangers"
    }

    # Call the continueStory function
    story_continuation = continueStory(progress, general_styles, player, player_input, keywords)
    print("Continued Story:", story_continuation)
