from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
import httplib2
from models import Log
from django.utils import timezone
import re
import json
from apiclient import discovery
from oauth2client import client, file
from . import sheet_settings

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = sheet_settings.CLIENT_SECRET_FILE
CREDENTIALS_FILE = sheet_settings.CREDENTIALS_FILE
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

	spreadsheetId = sheet_settings.FROM_SHEET
	output_spreadsheet = sheet_settings.TO_SHEET
	out = sheet_settings.TO_TAB
	tabs = sheet_settings.FROM_TABS

	http = CREDENTIALS.authorize(httplib2.Http())
	discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
	service = discovery.build("sheets", "v4", http=http, discoveryServiceUrl=discovery_url)

	range_pattern = re.compile(r"\w+!A(\d+):M")

	for tab in tabs:

		# Get recent Log
		recent_logs = Log.objects.order_by('-updated_at').filter(from_sheet=spreadsheetId, to_sheet=output_spreadsheet, from_tab=tab,
										   to_tab=out)
		last_log = Log(from_sheet=spreadsheetId, to_sheet=output_spreadsheet, from_tab=tab, to_tab=out)
		if recent_logs:
			last_log = recent_logs[0]
		start_row = range_pattern.findall(last_log.updated_range)
		offset = 2

		if not start_row:
			sheet_range = sheet_settings.RANGE.format(offset-1)
		else:
			start_row = start_row[0]
			offset = int(start_row) + last_log.updated_row
			sheet_range = sheet_settings.RANGE.format(offset)

		# Read Data from Sheet
		body = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
														range="%s!%s" % (tab, sheet_range)
														).execute()

		# Get the first Sheet value
		values = body.get("values", [])
		if not values:
			continue

		top_row = values.pop(0)
		# Remove the top headers
		while not top_row or top_row[0] == "":
			top_row = values.pop(0)

		# Iterate through each row
		for row_no, value in enumerate(values):

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
				# Push the data to sheet
				body = service.spreadsheets().values().update(spreadsheetId=output_spreadsheet,
															  range=out + '!A{}:M'.format(offset),
															  body={"values": [row]}, valueInputOption="RAW").execute()
				last_log = success_log(last_log, spreadsheetId=spreadsheetId,
									   output_spreadsheet=output_spreadsheet,
									   tab=tab,
									   out=out,
									   body=body)
			except:
				print "Error in Product:{}".format(product_id)
				# Push the data to sheet
				body = service.spreadsheets().values().update(spreadsheetId=output_spreadsheet,
															  range=out + '!A{}:M'.format(offset),
															  body={"values": [row]}, valueInputOption="RAW").execute()
				last_log = error_log(last_log, spreadsheetId=spreadsheetId,
										output_spreadsheet=output_spreadsheet,
										tab=tab,
										out=out,
										offset=offset)
			offset += 1
	return HttpResponse("Success")


def success_log(last_log, **params):
	spreadsheetId = params["spreadsheetId"]
	output_spreadsheet = params["output_spreadsheet"]
	tab = params["tab"]
	out = params["out"]
	body = params["body"]
	if last_log.status == "Success":
		last_log.updated_row += 1
		last_log.save()
	else:
		last_log = Log(from_sheet=spreadsheetId, to_sheet=output_spreadsheet, from_tab=tab, to_tab=out)
		last_log.updated_range = body["updatedRange"]
		last_log.updated_row = body["updatedRows"]
		last_log.updated_col = body["updatedColumns"]
		last_log.status = "Success"
		last_log.save()
	return last_log


def error_log(last_log, **params):
	spreadsheetId = params["spreadsheetId"]
	output_spreadsheet = params["output_spreadsheet"]
	offset = params["offset"]
	tab = params["tab"]
	out = params["out"]
	if last_log.status == "Error":
		last_log.updated_row += 1
		last_log.save()
	else:
		last_log = Log(from_sheet=spreadsheetId, to_sheet=output_spreadsheet, from_tab=tab, to_tab=out)
		last_log.updated_range = '!A{}:M'.format(offset)
		last_log.updated_row = 1
		last_log.updated_col = 0
		last_log.status = "Error"
		last_log.save()
	return last_log


def get_bike_details(bike_id):
	url = "https://api.credr.com/v1/product/vehicle/detail/{}/".format(bike_id)
	http = httplib2.Http()
	headers = {"Accept": "application/json", "X-Auth": "1234567890"}
	_, response = http.request(url, headers=headers)
	return json.loads(response)


def render_index(request):
	template_name = 'sheets_io/index.html'
	return render(request, template_name)
