from dotenv import load_dotenv
import os
import json

load_dotenv()
my_api_key = os.getenv("CLAUDE_API")


from anthropic import Anthropic

client = Anthropic(
    api_key=my_api_key
)




# Function to read the prompt template from a text file
def read_prompt_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to create the prompt by replacing placeholders
def create_prompt(passage, template,nos):
    prompt = template.replace("<passage>", passage)
    prompt = prompt.replace("<nos>",str(nos))
    return prompt

def extract_response_details_shortq(response_content):
    """
    Extracts 'question', 'options', and 'correct_answer' from a JSON array embedded in a string,
    by first identifying the start and end of the array enclosed in '[' and ']'.
    
    Args:
        response_content (str): The response content as a string containing a JSON array.
    
    Returns:
        list: A list of dictionaries containing 'question', 'options', and 'correct_answer', or None if parsing fails.
    """
    try:
        # Find the indices of the opening and closing brackets
        start_idx = response_content.find('[')
        end_idx = response_content.rfind(']')

        if start_idx != -1 and end_idx != -1:  # Ensure both brackets are found
            # Extract the JSON array portion of the response content
            valid_json_string = response_content[start_idx:end_idx+1]
            
            # Parse the JSON string into a Python list of dictionaries
            parsed_response = json.loads(valid_json_string)
            
            # List to store the extracted details
            extracted_details = []

            # Iterate over each question in the parsed JSON array
            for item in parsed_response:
                question = item.get("question")
                llm_answer = item.get("llm_answer")

                # Ensure all required fields are present
                if question is not None and llm_answer is not None:
                    extracted_details.append({
                        "question": question,
                        "llm_answer": llm_answer,
                    })

            if extracted_details:
                return extracted_details
        return None  # Return None if no valid data was extracted

    except json.JSONDecodeError:
        return None  # Return None if there is an error in decoding the JSON part
    
    
# Function to generate output based on inputs
def generate_shortq(context,nos):
    # Read the template from the file
    template = read_prompt_template("shortq_gen_prompt.txt")
    
    # Construct the prompt
    prompt = create_prompt(context, template,nos)
    
    retries = 5
    while retries > 0:
        retries -= 1
        # Make the API call
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # import pdb; pdb.set_trace()
        # Extract and parse the response

        extracted_details = extract_response_details_shortq(response.content[0].text)
        if extracted_details is not None:  # If valid JSON was extracted, return it
            return extracted_details
        
        # If retries are exhausted and no valid data is extracted
    raise ValueError("Failed to generate valid JSON response after multiple retries.")

# # Sample RUN
# passage = "The Document Object Model (DOM) is a programming interface for web documents. It represents the structure of a web page as a tree of objects, each corresponding to a part of the page, such as elements, attributes, and text content. In Angular, the DOM plays a crucial role in rendering components and handling user interactions. Angular’s change detection mechanism updates the DOM efficiently, ensuring that only the necessary elements are re-rendered when the component's data changes. This dynamic interaction between the component’s state and the DOM is at the core of Angular's declarative rendering approach. Furthermore, Angular provides tools like Renderer2 to safely interact with the DOM, which helps abstract away browser-specific differences and improves security by preventing potential cross-site scripting (XSS) vulnerabilities. Understanding how Angular interacts with the DOM is key to optimizing application performance and ensuring seamless user experiences."

# extracted_details= generate_shortq(passage,3)
# print(extracted_details)

# [
# {
# 	'question': 'What is the Document Object Model (DOM) and how does it represent a web page?',
# 	'llm_answer': 'The Document Object Model (DOM) is a programming interface for web documents. It represents the structure of a web page as a tree of objects, each corresponding to a part of the page, such as elements, attributes, and text content.'
# },
# {
# 	'question': 'What is the role of the DOM in Angular applications?',
# 	'llm_answer': "In Angular, the DOM plays a crucial role in rendering components and handling user interactions. Angular's change detection mechanism updates the DOM efficiently, ensuring that only the necessary elements are re-rendered when the component's data changes."
# },
# {
# 	'question': 'How does Angular interact with the DOM, and why is understanding this interaction important?',
# 	'llm_answer': 'Angular provides tools like Renderer2 to safely interact with the DOM, which helps abstract away browser-specific differences and improves security by preventing potential cross-site scripting (XSS) vulnerabilities. Understanding how Angular interacts with the DOM is key to optimizing application performance and ensuring seamless user experiences.'
# }]