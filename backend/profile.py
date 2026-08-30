from backend.database import initialize_database, create_beneficiary, get_beneficiary, get_beneficiary_for_user, update_beneficiary

def initialize_profile_system():
    initialize_database()

def create_profile(profile, user_id):
    i = create_beneficiary(user_id=user_id, **profile)
    return get_beneficiary(i)

def get_profile(beneficiary_id):
    return get_beneficiary(beneficiary_id)

def get_my_profile(user_id):
    return get_beneficiary_for_user(user_id)

def update_profile(beneficiary_id, profile, user_id):
    if not update_beneficiary(beneficiary_id, user_id, **profile):
        return None
    return get_beneficiary(beneficiary_id)
