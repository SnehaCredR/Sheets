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
	tabs = sheet_settings.FROM_TABS

	http = CREDENTIALS.authorize(httplib2.Http())
	discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
	service = discovery.build("sheets", "v4", http=http, discoveryServiceUrl=discovery_url)

	offset = 1

	for tab in tabs:
		# Read Data from Sheet
		body = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId,
														ranges="%s!%s" % (tab, sheet_range)
														).execute()

		# Get the first Sheet value
		values = body.get("valueRanges", [])[0]["values"]
		top_row = values.pop(0)

		# Remove the top headers
		while not top_row or top_row[0] == "":
			top_row = values.pop(0)

		# Iterate through each row
		for value in values:
			# Input Values from the sheet
			row = [value[0], value[1], value[3], value[4]]
			if len(value) <= 29:
				row.extend([""] * 3)
			elif len(value) <= 30:
				row.append(value[29])
				row.extend([""] * 2)
			else:
				row.append(value[29])
				row.append(value[30])
				if len(value) > 34:
					row.append(value[34])
				else:
					row.extend([""] * 1)

			product_id = row[3]
			try:
				# Read data from the details API
				detail = get_bike_details(product_id)
				row.append(detail["payload"]["make"])
				row.append(detail["payload"]["model"])
				row.append(detail["payload"]["date_of_mfg"])
				row.append("")
				row.append("")
				inspector = detail["payload"].get("inspector", "")
				if inspector:
					row.append(inspector["first_name"] + " " + inspector["last_name"])
				print "Uploaded Product:{}".format(product_id)
			except:
				print "Error in Product:{}".format(product_id)
			# Push the data to sheet
			body = service.spreadsheets().values().update(spreadsheetId=output_spreadsheet,
														  range=out + '!A{}:M'.format(offset + 1),
														  body={"values": [row]}, valueInputOption="RAW").execute()
			offset += 1
	return HttpResponse("Success")


def get_bike_details(bike_id):
	url = "https://api.credr.com/v1/product/vehicle/detail/{}/".format(bike_id)
	http = httplib2.Http()
	headers = {"Accept": "application/json", "X-Auth": "1234567890"}
	_, response = http.request(url, headers=headers)
	return json.loads(response)


