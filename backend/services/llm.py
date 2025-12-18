import json
from groq import Groq
from ..config import settings

# Initialize Groq Client
client = Groq(api_key=settings.GROQ_API_KEY)


def load_prompt_template() -> str:
    """Reads the static prompt prefix from the text file."""
    if not settings.PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Prompt file not found at {settings.PROMPT_PATH}")
    with open(settings.PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def generate_cover_letter_content(job_title: str, company_name: str, language: str, description: str, user_name: str = "") -> str:
    """
    Constructs the prompt and queries Groq (openai/gpt-oss-120b).
    Returns the raw body text of the cover letter.
    """
    system_instruction = load_prompt_template()

    # Construct the User Context
    user_context = f"""
    APPLICANT NAME: {user_name if user_name else "[Applicant Name]"}
    JOB DETAILS:
    Job Title: {job_title}
    Company: {company_name}
    Language required: {language}
    Job Description: {description}
    """

    try:
        print(f"Calling Groq ({settings.GROQ_MODEL}) for {company_name}...")

        # Call Groq API
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_instruction
                },
                {
                    "role": "user",
                    "content": user_context
                }
            ],
            temperature=0.7,             # Slightly creative but focused
            max_completion_tokens=8192,
            top_p=1,
            stream=True,                 # Streaming enabled as per your request
            stop=None
        )

        # 1. Accumulate the stream into a single string
        full_response = ""
        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content

        # 2. Post-processing (JSON Parsing)
        text_response = full_response.strip()

        # Clean Markdown formatting (e.g. ```json ... ```)
        if "```" in text_response:
            # Simple extraction: find the first { and last }
            start = text_response.find("{")
            end = text_response.rfind("}") + 1
            if start != -1 and end != -1:
                text_response = text_response[start:end]

        # 3. Parse JSON
        data = json.loads(text_response)

        # Return just the body content
        return data.get("cover_letter", "").replace('\n\n', '\n')

    except json.JSONDecodeError:
        print("Warning: Failed to parse JSON, returning raw text.")
        # If model failed to give JSON, return the raw text so user can edit it manually
        return text_response
    except Exception as e:
        raise RuntimeError(f"Groq API Error: {str(e)}")
