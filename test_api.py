from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say: API connection working"}]
)
print(response.content[0].text)
