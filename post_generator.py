from llm_helper import llm
from few_shot import FewShotPosts

few_shot = FewShotPosts()

def get_length_str(length):
    if length == "Short":
        return "1 to 5 lines"
    if length == "Medium":
        return "6 to 10 lines"
    if length == "Long":
        return "11 to 15 lines"

def get_prompt(length, language, tag):
    length_str = get_length_str(length)

    prompt = f'''
    Do not include any preamble, introductory sentences, or phrases like "Here's a blablabla". Just generate the content directly.

    1) Topic: {tag}
    2) Length: {length_str}
    3) Language: {language}

    If the language is "Indonesia":
    - Write fully in Bahasa Indonesia
    - Use natural Indonesian writing style, mixing formal and casual expressions as appropriate
    - Technical terms can remain in English when that's how they're commonly used in Indonesia
    - Use a conversational yet professional tone appropriate for LinkedIn
    - Include occasional emoji where it enhances the message
    - Structure content with clear paragraphs and occasional lists if needed

    If the language is "English":
    - Write entirely in English
    - Use professional yet approachable language
    - Avoid overly academic or stiff phrasing
    - Maintain a conversational tone that's appropriate for a professional platform
    - Include occasional emoji only when they add value to the content
    - Structure content clearly with proper formatting

    If the language is "Mixed":
    - Write primarily in Bahasa Indonesia (60-70%) mixed with casual English phrases or terms (30-40%)
    - Use a natural conversational Indonesian writing style similar to how young professionals communicate
    - Use shortened forms (like "yg", "gara2", "kalo", "ga/gak") only where it fits the flow and context. Don't use it if it's formal.
    - Incorporate English technical terms, industry jargon, and expressions naturally
    - Code-switch between languages in a way that feels authentic and natural
    - Include occasional emoji where appropriate when emphasizing points
    - Ensure the writing feels authentic to how Indonesian tech professionals naturally communicate
    - Maintain professional content while using a natural mix of formal and casual language
    '''

    examples = few_shot.get_filtered_posts(length, language, tag)
    print(examples)

    if len(examples) > 0:
        prompt += "4) Use the writing style as per the following examples."

    for i, post in enumerate(examples):
        post_text = post['post']
        prompt += f'\n\n Example {i+1}: \n\n {post_text}'

        if i == 1:
            break

    return prompt

def generate_post(length, language, tag):
    prompt = get_prompt(length, language, tag)
    response = llm.invoke(prompt)
    return response.content
