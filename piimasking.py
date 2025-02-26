import openai
import re

# OpenAI API key
OPENAI_API_KEY = "xx"

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# List of known company names
COMPANY_NAMES = ["Google", "Microsoft"]

def mask_pii(text):
    """Mask common PII and company names in user input before sending to OpenAI."""
    
    # Mask email addresses (Keep first and last letter before @, mask the rest)
    def mask_email(match):
        username = match.group(1)
        domain = match.group(2) + "." + match.group(3)
        if len(username) > 2:
            masked_username = username[0] + "*" * (len(username) - 2) + username[-1]
        else:
            masked_username = username[0] + "*"
        return f"{masked_username}@{domain}"
    
    text = re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+)\.([a-zA-Z]{2,})', mask_email, text)

    # Mask phone numbers
    text = re.sub(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}', '***-***-****', text)

    # Mask credit card numbers
    text = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '**** **** **** ****', text)

    # Mask social security numbers (SSN)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '***-**-****', text)

    # Mask addresses
    text = re.sub(r'\b\d{1,5}\s\w+\s(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Lane|Ln|Drive|Dr|Way|Court|Ct)\b', '*** [Redacted Address]', text, flags=re.IGNORECASE)

    # Mask company names, including inflected versions (like "Samsungu")
    for company in COMPANY_NAMES:
        text = re.sub(rf'\b{company}[a-zA-Z]*\b', '[Company]', text, flags=re.IGNORECASE)

    return text

def chat_with_gpt(user_input):
    """Send user input to OpenAI after PII masking and return only the response text."""
    masked_input = mask_pii(user_input)
    print(f"🔍 Masked Input Sent to OpenAI: {masked_input}")  # Debugging line
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": masked_input}]
    )
    return response.choices[0].message.content

# User input loop
while True:
    user_input = input("Mesajınızı girin ('çıkış' yazınca kapanır): ")
    
    if user_input.lower() == "çıkış":
        break

    response_text = chat_with_gpt(user_input)
    print("Yanıt:", response_text)
