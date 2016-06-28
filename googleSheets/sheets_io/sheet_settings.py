import os

FROM_SHEET = "1QnHjOvqH9kVU9mMTer_Pyc_1hMFkOKeKY2dDW0tAXJ8"
FROM_TABS = ['Input1', 'Input2']
RANGE = "A:G"

TO_SHEET = "1QnHjOvqH9kVU9mMTer_Pyc_1hMFkOKeKY2dDW0tAXJ8"
TO_TAB = 'Output'

CLIENT_SECRET_FILE = os.path.join(os.path.abspath('.'), 'credentials/client_secret.json')
CREDENTIALS_FILE = os.path.join(os.path.abspath('.'), 'credentials/credentials.json')