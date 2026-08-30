from pathlib import Path
import json
from fastapi import FastAPI, HTTPException, Depends, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from uuid import uuid4
from backend.database import initialize_database, create_chat_session, get_chat_session, save_chat_message, get_chat_messages, save_scheme, unsave_scheme, get_saved_schemes, get_nearby_partners

from backend.profile import initialize_profile_system, create_profile, get_profile, get_my_profile, update_profile
from backend.application import initialize_application_table, create_application, get_application, update_application_status, get_beneficiary_applications, application_owned_by_user
from backend.auth import initialize_auth_table, create_user, get_user, verify_password, create_access_token, decode_access_token
from ai.scheme_source import get_scheme_source
from ai.recommendation_service import get_recommendations as ai_recommendations, search_schemes as ai_search, check_single_scheme_eligibility

app=FastAPI(title='Scheme Sahayak AI - Government Scheme Assistant',version='3.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=False,allow_methods=['*'],allow_headers=['*'])
security=HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials=Security(security)):
    payload=decode_access_token(credentials.credentials)
    if not payload: raise HTTPException(401,'Invalid or expired token')
    return payload

def require_roles(*roles):
    def dep(user=Depends(get_current_user)):
        if user.get('role') not in roles: raise HTTPException(403,'Insufficient permissions')
        return user
    return dep

initialize_database(); initialize_auth_table(); initialize_profile_system(); initialize_application_table()
FEATURES_FILE=Path(__file__).resolve().parent.parent/'data'/'features.json'

class BeneficiaryProfile(BaseModel):
    category:str=Field(min_length=1)
    annual_income:float=Field(ge=0)
    age:int=Field(ge=0,le=120)
    purpose:str=Field(min_length=1)
    gender:str|None=None
    state:str|None=None
    district:str|None=None
    occupation:str|None=None
    business_type:str|None=None
    business_stage:str|None=None
class RecommendationRequest(BeneficiaryProfile): requested_amount:float=Field(gt=0)
class ApplicationRequest(BaseModel): beneficiary_id:int=Field(gt=0); scheme_id:str=Field(min_length=1); notes:str|None=None
class ApplicationStatusUpdate(BaseModel): status:str; notes:str|None=None
class RegisterRequest(BaseModel): username:str=Field(min_length=3,max_length=80); password:str=Field(min_length=8,max_length=128); role:str='beneficiary'
class LoginRequest(BaseModel): username:str; password:str

@app.get('/')
def root(): return {'project':'Scheme Sahayak AI','status':'running','platform':'AI Government Scheme Assistant','scheme_count':len(get_scheme_source().all()),'registered_features':317}
@app.get('/health')
def health(): return {'status':'healthy','scheme_count':len(get_scheme_source().all())}

@app.post('/api/auth/register')
def register_user(request:RegisterRequest):
    # Public registration is beneficiary-only. Privileged users must be provisioned securely.
    if request.role!='beneficiary': raise HTTPException(403,'Public registration can only create beneficiary accounts')
    user=create_user(request.username.strip(),request.password,'beneficiary')
    if user is None: raise HTTPException(409,'Username already exists')
    return {'message':'User registered successfully','user':user}

@app.post('/api/auth/login')
def login_user(request:LoginRequest):
    user=get_user(request.username.strip())
    if not user or not verify_password(request.password,user['password_hash']): raise HTTPException(401,'Invalid username or password')
    return {'message':'Login successful','access_token':create_access_token(user['id'],user['username'],user['role']),'token_type':'bearer','user':{'id':user['id'],'username':user['username'],'role':user['role']}}

@app.post('/api/auth/provision')
def provision_user(request:RegisterRequest,user=Depends(require_roles('admin'))):
    if request.role not in {'beneficiary','officer','admin'}: raise HTTPException(400,'Invalid role')
    created=create_user(request.username.strip(),request.password,request.role)
    if created is None: raise HTTPException(409,'Username already exists')
    return {'message':'User provisioned','user':created}

@app.get('/api/profiles/me')
def my_profile(user=Depends(get_current_user)):
    return {'profile':get_my_profile(int(user['sub']))}

@app.post('/api/profiles')
def create_beneficiary_profile(profile:BeneficiaryProfile,user=Depends(get_current_user)):
    saved=create_profile(profile.model_dump(),int(user['sub'])); return {'message':'Beneficiary profile created','profile':saved}

def owned_profile(profile_id,user):
    p=get_profile(profile_id)
    if not p: raise HTTPException(404,'Beneficiary profile not found')
    if p.get('user_id')!=int(user['sub']) and user.get('role') not in {'admin','officer'}: raise HTTPException(403,'You do not have access to this profile')
    return p

@app.get('/api/profiles/{profile_id}')
def get_beneficiary_profile(profile_id:int,user=Depends(get_current_user)): return {'profile':owned_profile(profile_id,user)}
@app.put('/api/profiles/{profile_id}')
def update_beneficiary_profile(profile_id:int,profile:BeneficiaryProfile,user=Depends(get_current_user)):
    if user.get('role') not in {'admin','officer'}: owned_profile(profile_id,user)
    updated=update_profile(profile_id,profile.model_dump(),int(user['sub']))
    if updated is None: raise HTTPException(404,'Beneficiary profile not found')
    return {'message':'Beneficiary profile updated','profile':updated}

@app.get('/api/features')
def get_features(user=Depends(get_current_user)):
    with open(FEATURES_FILE,encoding='utf-8') as f:r=json.load(f)
    return r
@app.get('/api/features/{feature_id}')
def get_feature(feature_id:str,user=Depends(get_current_user)):
    with open(FEATURES_FILE,encoding='utf-8') as f:r=json.load(f)
    for feature in r['features']:
        if feature['id'].lower()==feature_id.lower(): return feature
    raise HTTPException(404,f'Feature {feature_id} not found')

# Unified 4,693-scheme AI endpoints
@app.post('/api/eligibility/check')
def eligibility_check(profile:BeneficiaryProfile,user=Depends(get_current_user)):
    from ai.scheme_models import UserProfile
    u=UserProfile(category=profile.category,annual_income=int(profile.annual_income),age=profile.age,purpose=profile.purpose,location=None)
    source=get_scheme_source(); results=[]
    from ai.eligibility_engine import check_eligibility
    for s in source.all():
        r=check_eligibility(u,s).model_dump()
        r['eligible']=r['status']=='ELIGIBLE'
        r['scheme_name']=s.scheme_name
        r['reasons']=r.get('matched_rules',[]) + r.get('failed_rules',[]) + r.get('warnings',[])
        results.append(r)
    return {'profile':profile.model_dump(),'total_schemes_checked':len(results),'results':results}

@app.post('/api/recommendations')
def recommendations(request:RecommendationRequest,user=Depends(get_current_user)):
    from ai.api_models import RecommendRequest
    ai_req=RecommendRequest(category=request.category,annual_income=int(request.annual_income),age=request.age,purpose=request.purpose,loan_required=int(request.requested_amount),top_n=20)
    result=ai_recommendations(ai_req.to_profile(),top_n=20)
    # Keep frontend-compatible aliases while preserving the richer AI response.
    for i,r in enumerate(result['recommendations'],1):
        r['rank']=i; r['match_score']=r['score']; r['reasons']=r['why_recommended']
    return {**result,'profile':request.model_dump(),'requested_amount':request.requested_amount,'eligible_schemes':len(result['recommendations'])}

@app.get('/api/schemes/search')
def schemes_search(category:str|None=None,state:str|None=None,keyword:str|None=None):
    return ai_search(category=category,state=state,keyword=keyword)
@app.get('/api/partners/nearby')
def nearby_partners(scheme_id: str, latitude: float, longitude: float, radius_km: float = 50):
    if not get_scheme_source().get(scheme_id):
        raise HTTPException(404, 'Scheme not found')
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise HTTPException(400, 'Invalid coordinates')
    radius_km = min(max(radius_km, 1), 100)
    return {'scheme_id': scheme_id, 'radius_km': radius_km,
            'partners': get_nearby_partners(scheme_id, latitude, longitude, radius_km=radius_km)}

@app.get('/api/schemes/{scheme_id}')
def scheme_detail(scheme_id:str):
    s=get_scheme_source().get(scheme_id)
    if not s: raise HTTPException(404,'Scheme not found')
    return {'scheme':s}

@app.post('/api/ai/chat')
def embedded_ai_chat(payload: dict, user=Depends(get_current_user)):
    """Grounded conversational assistant with persistent SQLite chat history."""
    from backend.ai_assistant import respond
    message = str(payload.get("message") or "").strip()
    if not message:
        raise HTTPException(400, "Please enter a message.")
    session_id = str(payload.get("session_id") or uuid4())
    scheme_id = payload.get("scheme_id")
    language = str(payload.get("language") or "en")
    if not get_chat_session(session_id, int(user["sub"])):
        create_chat_session(session_id, int(user["sub"]), scheme_id, language)
    save_chat_message(session_id, "user", message)
    result = respond(message, int(user["sub"]), language, scheme_id, get_chat_messages(session_id, 12))
    save_chat_message(session_id, "assistant", result["reply"])
    result.update({"session_id": session_id, "history": get_chat_messages(session_id, 30)})
    return result

@app.get('/api/ai/history/{session_id}')
def ai_history(session_id:str, user=Depends(get_current_user)):
    if not get_chat_session(session_id, int(user["sub"])):
        raise HTTPException(404, "Chat session not found")
    return {"session_id":session_id, "messages":get_chat_messages(session_id, 100)}

@app.get('/api/saved')
def saved_schemes(user=Depends(get_current_user)):
    return {"saved":get_saved_schemes(int(user["sub"]))}

@app.post('/api/saved/{scheme_id}')
def save_one_scheme(scheme_id:str, user=Depends(get_current_user)):
    if not get_scheme_source().get(scheme_id): raise HTTPException(404,"Scheme not found")
    save_scheme(int(user["sub"]), scheme_id)
    return {"message":"Scheme saved","scheme_id":scheme_id}

@app.delete('/api/saved/{scheme_id}')
def unsave_one_scheme(scheme_id:str, user=Depends(get_current_user)):
    unsave_scheme(int(user["sub"]), scheme_id)
    return {"message":"Scheme removed","scheme_id":scheme_id}

@app.get('/api/database/status')
def database_status(user=Depends(require_roles('admin','officer'))):
    from backend.database import DATABASE_FILE
    return {"status":"connected","engine":"SQLite","database":str(DATABASE_FILE),"tables":["users","beneficiaries","applications","saved_schemes","notifications","chat_sessions","chat_messages","partners"]}


@app.post('/api/applications')
def submit_application(application:ApplicationRequest,user=Depends(get_current_user)):
    profile=owned_profile(application.beneficiary_id,user)
    if not get_scheme_source().get(application.scheme_id): raise HTTPException(404,'Scheme not found')
    created=create_application(application.beneficiary_id,application.scheme_id,application.notes)
    return {'message':'Application submitted successfully','application':created}
@app.get('/api/applications/{application_id}')
def get_application_details(application_id:int,user=Depends(get_current_user)):
    a=application_owned_by_user(application_id,int(user['sub']))
    if not a and user.get('role') not in {'admin','officer'}: raise HTTPException(403,'You do not have access to this application')
    a=a or get_application(application_id)
    if not a: raise HTTPException(404,'Application not found')
    return {'application':a}
@app.put('/api/applications/{application_id}/status')
def change_application_status(application_id:int,status_update:ApplicationStatusUpdate,user=Depends(require_roles('admin','officer'))):
    allowed={'submitted','under_review','approved','rejected','completed'}
    if status_update.status not in allowed: raise HTTPException(400,'Invalid status')
    current=get_application(application_id)
    if not current: raise HTTPException(404,'Application not found')
    transitions={'submitted':{'under_review','rejected'},'under_review':{'approved','rejected'},'approved':{'completed'},'rejected':set(),'completed':set()}
    if status_update.status not in transitions[current['status']]: raise HTTPException(409,f"Invalid status transition from {current['status']} to {status_update.status}")
    return {'message':'Application status updated','application':update_application_status(application_id,status_update.status,status_update.notes)}
@app.get('/api/profiles/{profile_id}/applications')
def get_profile_applications(profile_id:int,user=Depends(get_current_user)):
    owned_profile(profile_id,user); apps=get_beneficiary_applications(profile_id); return {'beneficiary_id':profile_id,'total_applications':len(apps),'applications':apps}

