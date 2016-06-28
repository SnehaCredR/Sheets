import os

FROM_SHEET = "1VBRX1BO5HBEaCaurkF2I4KkUusIN7ZjGq6Oa_r4Iijw"
FROM_TABS = ['Bangalore', 'Mumbai', 'Delhi', 'Hyderabad', 'Pune']
RANGE = "A:E"

TO_SHEET = "1VBRX1BO5HBEaCaurkF2I4KkUusIN7ZjGq6Oa_r4Iijw"
TO_TAB = 'Tool'

CLIENT_SECRET_FILE = os.path.join(os.path.abspath('.'), 'credentials/client_secret.json')
CREDENTIALS_FILE = os.path.join(os.path.abspath('.'), 'credentials/credentials.json')