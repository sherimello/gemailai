from fastapi import FastAPI, Body
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import json

app = FastAPI()

# Define the functions
def send_email(subject, body, to_email, from_email, app_password):
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Set up the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, app_password)

        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")

def get_payload(data):
    payload = {
        "messages": [
            {"content": data, "role": "user"},
            # Add other messages here if needed
        ],
        "id": "W8oxIjG",
        "previewToken": None,
        "agentMode": {},
        "clickedAnswer2": False,
        "clickedAnswer3": False,
        "codeModelMode": False,
        "githubToken": None,
        "isChromeExt": False,
        "isMicMode": False,
        "trendingAgentMode": {},
        "userId": "bdcea0a8-7eb1-46d7-9129-0109a2597718",
        "visitFromDelta": None
    }

    return payload

def remove_empty_lines(text):
    lines = text.split("\n")

    # Remove empty lines
    non_empty_lines = [line for line in lines if line.strip()!= '']

    # Join the non-empty lines back into a single string
    result_string = '\n'.join(non_empty_lines)
    return result_string

def get_json_formatted_text(key_name):
    ai_generated_result = get_mail(key_name)
    json_formatted_string = "{\n" + ai_generated_result[ai_generated_result.index("\"subject\": "):].replace("```", "")

    if """"}""" in json_formatted_string:
        json_formatted_string = json_formatted_string.replace(""""}""", """"\n}""")

    json_formatted_string = json_formatted_string[
                            0: json_formatted_string.index(""""body":""")] + json_formatted_string[
                                                                             json_formatted_string.index(
                                                                                 """"body":"""): json_formatted_string.index(
                                                                                 """\n}""")].replace("\n",
                                                                                                     "\\n") + "\n}"

    return json_formatted_string

def get_mail(optimized_prompt: str):
    structure_instruction = """. give only the copyable output in this format: {"subject": subject, "body": body}"""

    response = requests.post("https://www.blackbox.ai/api/chat", headers={'Content-Type': 'application/json'}, json=get_payload(optimized_prompt + structure_instruction))

    return remove_empty_lines(response.text)

def convert_user_input_into_ai_prompt_and_get_mail(user_input: str):
    s1 = """{ "prompt": "Optimize the following prompt without executing it and return just the copyable json:
    '"""
    s2 = """'

***DONT WRITE THE EMAIL. JUST OPTIMIZE THE PROMPT AND DONT GIVE ANY EXPLANATIONS***
" }"""

    response = requests.post("https://www.blackbox.ai/api/chat", json=get_payload(s1 + user_input + s2),
                             headers={'Content-Type': 'application/json'})
    try:
        cleaned_prompt_json = """{
        """ + response.text[response.text.index("\"prompt\":"):]
        if "```" in cleaned_prompt_json:
            cleaned_prompt_json = cleaned_prompt_json.replace("```", "")

        json_resp = json.loads(cleaned_prompt_json)
        keys = list(json_resp.keys())

        json_formatted_string = get_json_formatted_text(json_resp[keys[0]])

        json_result = json.loads(json_formatted_string)
        return json_result
    except json.JSONDecodeError as e:
        json_error_message = "{\n\"error_message\": " + str(e) + "\n}"
        return {"error": e.msg}

# Define the endpoints
@app.post("/process_input")
async def process_input(user_input: str):
    return convert_user_input_into_ai_prompt_and_get_mail(user_input)

@app.post("/send")
async def send(subject: str, body: str, to_email: str, from_email: str, app_password: str):
    send_email(subject, body.replace("\\n", """
"""), to_email, from_email, app_password)
    return {"message":"Email sent successfully!"}