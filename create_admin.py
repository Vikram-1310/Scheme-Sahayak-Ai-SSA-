import getpass
from backend.auth import initialize_auth_table, create_user, get_user
initialize_auth_table()
username=input('Admin username: ').strip()
password=getpass.getpass('Admin password (8+ chars): ')
if len(password)<8: raise SystemExit('Password must be at least 8 characters.')
if get_user(username): raise SystemExit('Username already exists.')
print(create_user(username,password,'admin'))
