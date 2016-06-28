from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

import httplib2
import os
import json

from apiclient import discovery
from oauth2client import client, file

from . import sheet_settings

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = sheet_settings.CLIENT_SECRET_FILE
CREDENTIALS_FILE = sheet_settings.CREDENTIALS_FILE
FLOW = client.flow_from_clientsecrets(CLIENT_SECRET_FILE,
									  scope=SCOPES,
									  redirect_uri="/sheets/index")
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

	spreadsheetId = sheet_settings.FROM_SHEET
	output_spreadsheet = sheet_settings.TO_SHEET
	out = sheet_settings.TO_TAB
	sheet_range = sheet_settings.RANGE
	cities = sheet_settings.FROM_TABS

	http = CREDENTIALS.authorize(httplib2.Http())
	discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
	service = discovery.build("sheets", "v4", http=http, discoveryServiceUrl=discovery_url)

	input_mat = []

	body = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
													ranges=[ "%s!%s" % (city, sheet_range) for city in cities]
													).execute()
	for valueRange in body["valueRanges"]:
		values = valueRange.get("values", [])
		for value in values[:]:
			top_row = values.pop(0)
			if not top_row or top_row[0] == "":
				continue
			break
		input_mat.extend(values)

	output = "Read data from Sheet:{} <br/> {}".format(spreadsheetId, len(input_mat))

	body = service.spreadsheets().values().update(spreadsheetId=output_spreadsheet, range=out + '!A7:E', body ={"values": input_mat }, valueInputOption = "RAW").execute()
	output += '<br/><br/>Data after writing to Sheet:{} <br/> {}'.format(output_spreadsheet, json.dumps(body))
	return HttpResponse(output)
