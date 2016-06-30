import os

FROM_SHEET = "1VBRX1BO5HBEaCaurkF2I4KkUusIN7ZjGq6Oa_r4Iijw"
FROM_TABS = ['Bangalore', 'Mumbai', 'Delhi']
RANGE = "A{}:AI"

TO_SHEET = "1QnHjOvqH9kVU9mMTer_Pyc_1hMFkOKeKY2dDW0tAXJ8"
TO_TAB = 'Output'
SHEET_OFFSET = 2

CLIENT_SECRET_FILE = os.path.join(os.path.abspath('.'), 'credentials/client_secret.json')
CREDENTIALS_FILE = os.path.join(os.path.abspath('.'), 'credentials/credentials.json')