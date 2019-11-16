"""A privacy.com API wrapper."""
from privacy.api_client import APIClient as Client

client = Client("5923e5cf-cb3f-473c-90d3-2bfa8304ae36", sandboxed=True)
cards = client.cards_list(page_size=1)
for card in cards:
    print(card)