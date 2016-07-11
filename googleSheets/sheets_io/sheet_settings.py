import os

FROM_SHEET = "15cuTVdn0kYaXqL_HdQRLqDmuMLO9xAAyansc79nE41s"
FROM_TABS = ['Bangalore', 'Mumbai', 'Delhi', 'Hyderabad', 'Pune' ]
RANGE = "A{}:AI"

TO_SHEET = "1QnHjOvqH9kVU9mMTer_Pyc_1hMFkOKeKY2dDW0tAXJ8"
TO_TAB = 'Output'
SHEET_OFFSET = 2

CLIENT_SECRET_FILE = os.path.join(os.path.abspath('.'), 'credentials/client_secret2.json')
CREDENTIALS_FILE = os.path.join(os.path.abspath('.'), 'credentials/credentials.json')