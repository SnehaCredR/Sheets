from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

import httplib2
import os
import json

from oauth2client import client, file

from . import google_auth as gauth


SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = os.path.join(os.path.abspath('.'), 'credentials/client_secret.json')
CREDENTIALS_FILE = os.path.join(os.path.abspath('.'), 'credentials/credentials.json')
FLOW = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
									  scope=SCOPES,
									  redirect_uri="http://localhost:8000/sheets/index")
STORAGE = file.Storage(CREDENTIALS_FILE)
CREDENTIALS = STORAGE.get()


def auth(request):
	global CREDENTIALS
	auth_uri = FLOW.step1_get_authorize_url()
	if CREDENTIALS and not CREDENTIALS.invalid:
		return HttpResponseRedirect(reverse("sheets_io:index"))
	return HttpResponseRedirect(auth_uri)


def index(request):
	global CREDENTIALS
	code = request.GET.get("code", "")
	if request.GET.get("error", ""):
		return HttpResponse("Error")
	if code:
		CREDENTIALS = FLOW.step2_exchange(code)
		STORAGE.put(CREDENTIALS)

	http = CREDENTIALS.authorize(httplib2.Http())

	# spreadsheetId = "1QqaElHbfvp-sRlG6A5NXBZb8-PsoPmq4wy3AGRlJ9OU"
	spreadsheetId = "1PcMvN7940wtFR1cRD88I3U_qEcq-6VfFDYAaVoXP_K4"
	sheet_range = "A:E"

	# response, body = gauth.getSheet(http, spreadsheetId, sheet_range)

	updSheet = gauth.updateSheet(http, spreadsheetId)
	updSheet.updateCells([["A", "B", "C"], ["D", "E", "F"]], 0, (6, 0))
	_, body = updSheet.execute()

	return HttpResponse(json.dumps(body))

