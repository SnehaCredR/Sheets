#!/usr/bin/python2 -tt

import json


def getSheet(http, sheet_id, sheet_range):
	url = "https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}".format(sheet_id, sheet_range)
	response, content = http.request(uri=url, method="GET")
	return response, json.loads(content)


class updateSheet:

	def __init__(self, http, sheet_id, data=dict()):
		self.http = http
		self.sheet_id = sheet_id
		self.url = "https://sheets.googleapis.com/v4/spreadsheets/{}:batchUpdate".format(sheet_id)
		self.modif_data = data
		self.data = {"requests": self.modif_data}

	def execute(self):
		print json.dumps(self.data)
		response, content = self.http.request(uri=self.url, method="POST", body=json.dumps(self.data))
		return response, json.loads(content)

	def updateCells(self, data, sheetNo=None, coords=None):
		if "updateCells" not in self.modif_data:
			self.modif_data["updateCells"] = {}
		put_data = self.modif_data["updateCells"]

		if sheetNo != None:
			if "start" in put_data:
				put_data["start"]["sheetId"] = sheetNo
			else:
				put_data["start"] = {"sheetId": sheetNo}

		if coords != None:
			if "start" in put_data:
				put_data["start"]["rowIndex"] = coords[0]
				put_data["start"]["columnIndex"] = coords[1]
			else:
				put_data["start"] = {"rowIndex": coords[0], "columnIndex": coords[1]}

		row_values = []
		for row in data:
			temp = {"values": []}
			for col in row:
				temp["values"].append({"userEnteredValue": {"stringValue": str(col)}})
			row_values.append(temp)

		if "rows" in put_data:
			put_data["rows"].extend(row_values)
		else:
			put_data["rows"] = row_values

		put_data['fields'] = 'userEnteredValue'








