from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

import httplib2
import os
import json

from apiclient import discovery
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
	discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
	service = discovery.build("sheets", "v4", http=http, discoveryServiceUrl=discovery_url)

	# spreadsheetId = "1QqaElHbfvp-sRlG6A5NXBZb8-PsoPmq4wy3AGRlJ9OU"
	# spreadsheetId = "1PcMvN7940wtFR1cRD88I3U_qEcq-6VfFDYAaVoXP_K4"

	# input_spreadsheets = ["1UmwLtvxpgiHOjlYG0HxWtz6E5Cjz-FNzgtq3W3CKOA8",
	# 					"1a6cx6OUBg5ZTio_GGhz5pPoe_yjVLZyK6sOwNdq-Pno",
	# 					"1QMFSifwgRcrsdStl-qdERdxwx9xrgfJcHY7hD8Fuom0"]
	input_spreadsheets = ["1VBRX1BO5HBEaCaurkF2I4KkUusIN7ZjGq6Oa_r4Iijw"]

	output_spreadsheet = "1VI2M5t5pBlA71aFAaMEmo_pN83_r9Y8LN4llBlU2oHw"
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
			# _, body = gauth.getSheet(http, spreadsheetId, sheet_range, sheet_name=city)
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
	#
	# output += "<br/><br/>Data after writing to Sheet:{} <br/> {}".format(output_spreadsheet, json.dumps(body))

	return HttpResponse(output)
