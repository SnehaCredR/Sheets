from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

import httplib2
import os
import json

from apiclient import discovery
from oauth2client import client, file


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
	discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
	service = discovery.build("sheets", "v4", http=http, discoveryServiceUrl=discovery_url)

	# input_spreadsheets = ["1UmwLtvxpgiHOjlYG0HxWtz6E5Cjz-FNzgtq3W3CKOA8",
	# 					"1a6cx6OUBg5ZTio_GGhz5pPoe_yjVLZyK6sOwNdq-Pno",
	# 					"1QMFSifwgRcrsdStl-qdERdxwx9xrgfJcHY7hD8Fuom0"]
	input_spreadsheets = ["1VBRX1BO5HBEaCaurkF2I4KkUusIN7ZjGq6Oa_r4Iijw"]

	output_spreadsheet = "1VBRX1BO5HBEaCaurkF2I4KkUusIN7ZjGq6Oa_r4Iijw"
	out = 'Tool'
	sheet_range = "A:E"
	input_mat = []

	cities = ['Bangalore', 'Mumbai', 'Delhi', 'Hyderabad', 'Pune']

	for spreadsheetId in input_spreadsheets:
		body = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
														ranges=[ "%s!%s" % (city, sheet_range) for city in cities]
														).execute()
		valueRanges = body["valueRanges"]
		# print valueRanges[0]
		for valueRange in valueRanges:
			values = valueRange.get("values", [])
			for value in values[:]:
				top_row = values.pop(0)
				if not top_row or top_row[0] == "":
					continue
				break
			input_mat.extend(values)


	output = "Read data from Sheet:{} <br/> {}".format(', '.join(input_spreadsheets), len(input_mat))

	# updSheet = gauth.updateSheet(http, output_spreadsheet)
	# updSheet.updateCells(input_mat, 0, (0, 0))
	# _, body = updSheet.execute()
	body = service.spreadsheets().values().update(spreadsheetId=output_spreadsheet, range=out + '!A7:E', body ={"values": input_mat }, valueInputOption = "RAW").execute()
	output += '<br/><br/>Data after writing to Sheet:{} <br/> {}'.format(output_spreadsheet, json.dumps(body))
	return HttpResponse(output)
