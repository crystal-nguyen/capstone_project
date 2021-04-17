import urllib.request
import os
import ssl
import json
import base64
import pandas as pd


class AzureModels:

    def __init__(self):
        pass

    def formatHistopathData(self, image_path):
        img = {}

        # Encode the image into bytes then readable ascii
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            ascii_string = encoded_string.decode('ascii')

        # String that describes the encoded image
        x = image_path.split(".")
        file_extension = x[-1]
        image_string = 'data:image/' + str(file_extension) + ";base64," + ascii_string

        # Build the JSON object
        data = {'Inputs': {"WebServiceInput0": [{'image': image_string, 'id': "0", 'category': "has_tumor"}]},
                'GlobalParameters': {}}
        json_data = json.dumps(data)
        # print(json_data)
        return json_data

    # Pass in path to the csv file and the respective row to
    # test the model with
    def formatOsteosarcomaData(self, csv):
        # Read CSV file
        df = pd.read_csv(csv)

        # Parses column headers
        headers = list(df.columns.values)

        # Ignore class label and useless headers
        temp = headers[3:11]
        temp.append(headers[13])
        temp.extend(headers[15:-1])
        headers = temp

        # Pull data at specified row
        row_data = df.iloc[0].values

        # Ignore class label and useless headers
        row_data = row_data[3:-1]

        # JSON string
        data = {"data": []}
        data_array = {}

        for i in range(0, len(headers)):
            # Fill in the column w/ respective row value
            data_array.setdefault(headers[i], str(row_data[i]))
        data["data"] = [data_array]

        # Build the JSON object
        json_data = json.dumps(data)
        # print(json_data)
        return json_data

    def allowSelfSignedHttps(allowed):
        # bypass the server certificate verification on client side
        if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
            ssl._create_default_https_context = ssl._create_unverified_context

    allowSelfSignedHttps(True)  # this line is needed if you use self-signed certificate in your scoring service.

    def sendOsteoData(self, json_data):
        # Create body of request using JSON
        body = str.encode(json_data)

        url = 'http://71f4100f-6fb1-434b-8192-fe31a645f92e.westus.azurecontainer.io/score'
        api_key = ''
        headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + api_key)}
        req = urllib.request.Request(url, body, headers)

        # Sending the request to the endpoint
        try:
            response = urllib.request.urlopen(req)
            result = response.read()
            result = result.decode('ascii')
            return result
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - includes the request ID and the timestamp for debugging failures
            print(error.info())
            print(json.loads(error.read().decode("utf8", 'ignore')))
            return None

    def sendHistoData(self, json_data):
        # Create body of request using JSON
        body = str.encode(json_data)

        # Default to the histopath data set
        url = 'http://104.45.231.141:80/api/v1/service/histopath-endpoint/score'
        api_key = '1ndWlDJMuzRU8Cpgf3NFD15jS0bEf93a'
        headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + api_key)}
        req = urllib.request.Request(url, body, headers)

        # Sending the request to the endpoint
        try:
            response = urllib.request.urlopen(req)
            result = response.read()
            result = result.decode('ascii')
            return result
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))
            # Print the headers - includes the request ID and the timestamp for debugging failures
            print(error.info())
            print(json.loads(error.read().decode("utf8", 'ignore')))
            return None

    def consumeEndpoints(self, osteo_data, histo_data):
        osteo_response = self.sendOsteoData(osteo_data)
        histo_response = self.sendHistoData(histo_data)
        return [osteo_response, histo_response]

    # Response[0] = osteo
    # Response[1] = histo
    def sanitizeResponses(self, responses):
        # Sanitize body of result
        osteo_response = responses[0]
        histo_response = responses[1]

        # "{\"result\", [\"Non-Tumor\"]}"
        osteo_split = osteo_response.split(":")
        temp = osteo_split[1]
        temp = temp.replace('"', '')
        temp = temp.replace('[', '')
        temp = temp.replace('\\', '')

        # osteo_result = Non-Tumor
        osteo_result = temp.rstrip('}]')

        # ["0", "Scored Probabilities_has_tumor"], [0.871647298336029, "Scored Probabilities_no_tumor"], [0.12835265696048737, "Scored Labels"], "has_tumor"}]}}
        histo_split = histo_response.split(":")
        histo_split = histo_split[4:]

        histo_result = []
        for i in range(0, len(histo_split)):
            temp = histo_split[i].split(",")
            histo_result.append(temp[0])
            if len(temp) > 1:
                histo_result.append(temp[1])
        histo_result = histo_result[1:]

        # Cleans: "has_tumor"}]}}
        temp = histo_result[-1].replace('}', '')
        temp = temp.replace(']', '')
        histo_result[-1] = temp

        # histo_result = "Scored Probabilities_has_tumor", 0.871647298336029, "Scored Probabilities_no_tumor", 0.12835265696048737, "Scored Labels", "has_tumor"
        return [osteo_result, histo_result]