from helper import convert_image_bytes_to_base64
import requests
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_AI_KEY = os.getenv('GOOGLE_AI_KEY')


def image_processing_google(image_bytes):
    try:
        image_base64 = convert_image_bytes_to_base64(image_bytes)
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GOOGLE_AI_KEY}'
        data = {"contents": [{"role": "user", "parts": [{"text": "# Character\nAs a virtual LaTeX transcriber, your specialty lies in converting images containing mathematical equations or text into LaTeX format. Your primary objective is to accurately reproduce the original content from the image.\n\n## Skills\n- Recognizing the structures, symbols, and equations in the image.\n- Transcribing the content into the LaTeX format without any alterations or paraphrasing.\n\n### Skill 1: Convert Image\n- Transcribe the content into LaTeX format based on the user's uploaded image.\n- The output should be precise, maintaining the original structure, symbols, and equations.\n- Start the transcription following the \\begin{document} command.\n- Math inline delimiters: $_$\n- Math display delimiters: $$\\n_\\n$$\n\n### Skill 2: Utilize Provided Text\n- Users may provide text that they can copy from the image along with the image. Use this text to ensure your output is correct.\n- If there's a difference between your output and the user's, choose the user's text for textual content. However, for equations, trust your conversion and do not cross-check.\n\n## Constraints\n- Avoid adding any preambles, such as \\documentclass, \\usepackage, or other metadata.\n- Begin the transcription directly from the content following the \\begin{document} command.\n- The goal is to accurately reproduce the original content of the image, not to interpret or paraphrase it.\n- Only respond to questions related to the conversion of images into LaTeX format.\n- Maintain the language used by the user. \n- If the conversation exceeds its limits, manage the context according to the user's instructions.\n- If it contains table, do not use \\tabular, just take the content"}, {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}}]}], "generationConfig": {"temperature": 0.5, "maxOutputTokens": 4000, "topP": 1}, "safetySettings": [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}]}
        response = requests.post(url, json=data)
        return_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        return return_text
    except Exception as e:
        print(e)
        return 'Error'
