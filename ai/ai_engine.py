"""Deterministic, dependency-free scheme assistant for the demo build."""
from ai.scheme_source import get_scheme_source

def chat_response(message:str):
    message=(message or '').strip()
    if not message: return {'status':'error','message':'Please enter a message.'}
    source=get_scheme_source(); results=source.search(message)[:5]
    if results:
        return {'status':'success','message':f'I found {len(results)} relevant scheme(s) matching your message.','schemes':[{'scheme_id':s.scheme_id,'scheme_name':s.scheme_name,'benefits':s.benefits,'application_url':s.application_url,'official_source':s.official_source} for s in results]}
    return {'status':'success','message':'Tell me your category, location, annual income, purpose, and required loan amount. I can then narrow down suitable government schemes.','schemes':[]}


def process_message(message: str):
    """Stable public entry point used by the standalone AI service."""
    return chat_response(message)

def chat(message: str):
    return chat_response(message)
