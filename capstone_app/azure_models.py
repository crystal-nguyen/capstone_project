import urllib.request
import os
import ssl
import json
import base64
import pandas as pd
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO


class AzureModels:

    def __init__(self):
        pass

    def formatImageData(self, image):
        img = {}

        # Encode the image into bytes then readable ascii
        encoded_string = base64.b64encode(image.read())
        ascii_string = encoded_string.decode('ascii')

        # String that describes the encoded image
        name, extension = os.path.splitext('testPNG.PNG')
        extension = (str(extension).lower())[1:]
        image_string = 'data:image/' + extension + ";base64," + ascii_string

        # Build the JSON object
        data = {'Inputs': {"WebServiceInput0": [{'image': image_string, 'id': "0", 'category': "has_tumor"}]},
                'GlobalParameters': {}}
        # print(json_data)
        return data

    # Pass in path to the csv file and the respective row to
    # test the model with
    def formatTabularData(self, csv):

        # convert file to StringIO
        csv_io = StringIO(csv.read().decode('ISO-8859-1'))

        # create dataframe
        csv_df = pd.read_csv(csv_io)
        # Pull data at specified row
        sample = csv_df.iloc[0].values

        # build dictionary
        data_dict = {}
        for i in range(len(csv_df.columns)):
            try:
                data_dict[csv_df.columns[i]] = int(sample[i])
            except:
                data_dict[csv_df.columns[i]] = sample[i]
        data = {"Inputs": {"input1": [data_dict], }, "GlobalParameters": {}}

        # Build the JSON object
        return data

    def allowSelfSignedHttps(allowed):
        # bypass the server certificate verification on client side
        if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
            ssl._create_default_https_context = ssl._create_unverified_context

    allowSelfSignedHttps(True)  # this line is needed if you use self-signed certificate in your scoring service.

    def sendTabularData(self, json_data):
        # Create body of request using JSON
        body = str.encode(json.dumps(json_data))

        url = 'http://6276f964-4ea6-42e2-bed7-cbccc13f92c6.westus.azurecontainer.io/score'
        api_key = 'VhaeYY8hwU42IBGgzaAIVRHwGHWYdm3n'  # Replace this with the API key for the web service
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

    def sendImageData(self, json_data):
        # Create body of request using JSON
        body = str.encode(json.dumps(json_data))
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

    def formatCombinedData(self, csv_response, image_response):
        csv_json_obj = json.loads(csv_response)
        image_json_obj = json.loads(image_response)

        columns=['Image Scored Probabilities_has_tumor','Image Scored Probabilities_no_tumor', 'Tabular Scored Probabilities_has_tumor','Tabular Scored Probabilities_no_tumor','Actual Class']
        csv_body = csv_json_obj["Results"]["WebServiceOutput0"][0]
        csv_tumor = csv_body['Scored Probabilities_has_tumor']
        csv_no_tumor = csv_body['Scored Probabilities_no_tumor']

        image_body = image_json_obj["Results"]["WebServiceOutput0"][0]
        image_tumor = image_body['Scored Probabilities_has_tumor']
        image_no_tumor = image_body['Scored Probabilities_no_tumor']

        data = [image_tumor, image_no_tumor, csv_tumor, csv_no_tumor,'class']
        combined_df = pd.DataFrame(columns=columns, data=[data])

        result = {}
        for i in range(len(combined_df.columns)):
            result[combined_df.columns[i]] = combined_df.iloc[0][i]

        data = {"Inputs": {"WebServiceInput0": [result], },"GlobalParameters": {}}

        return data

    def sendCombinedData(self, json_data):
        body = str.encode(json.dumps(json_data))

        url = 'http://0352ffb7-e19c-4307-af73-7ed824ed1b39.westus.azurecontainer.io/score'
        api_key = 'B1ndv3rJho7mIjFZypSWhmN3phyLuDCv'  # Replace this with the API key for the web service
        headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + api_key)}

        req = urllib.request.Request(url, body, headers)

        try:
            response = urllib.request.urlopen(req)
            result = response.read()
            result = result.decode('ascii')
            return result
        except urllib.error.HTTPError as error:
            print("The request failed with status code: " + str(error.code))

            # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
            print(error.info())
            print(json.loads(error.read().decode("utf8", 'ignore')))

    def tabularModel(self, csv_file):

        # format data
        csv_json = self.formatTabularData(csv_file)
        csv_response = self.sendTabularData(csv_json)
        return csv_response

    def imageModel(self, image_file):

        # format data
        image_json = self.formatImageData(image_file)
        image_response = self.sendImageData(image_json)
        return image_response

    def combinedModel(self, csv_file, image_file):

        #get the individual model responses
        tabular_response = self.tabularModel(csv_file)
        image_response = self.imageModel(image_file)
        combined_json = self.formatCombinedData(tabular_response, image_response)
        combined_response = self.sendCombinedData(combined_json)
        combined_response_dict = json.loads(combined_response)
        result = combined_response_dict["Results"]["WebServiceOutput0"][0]["Scored Labels"]
        return result



