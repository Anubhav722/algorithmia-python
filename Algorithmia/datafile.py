'Algorithmia Data API Client (python)'

import re
import json
import six
import tempfile
from datetime import datetime

from Algorithmia.util import getParentAndBase
from Algorithmia.data import DataObject, DataObjectType

class DataFile(DataObject):
    def __init__(self, client, dataUrl):
        super(DataFile, self).__init__(DataObjectType.file)
        self.client = client
        # Parse dataUrl
        self.path = re.sub(r'^data://|^/', '', dataUrl)
        self.url = '/v1/data/' + self.path
        self.last_modified = None
        self.size = None

    def set_attributes(self, attributes):
        self.last_modified = datetime.strptime(attributes['last_modified'],'%Y-%m-%dT%H:%M:%S.000Z')
        self.size = attributes['size']

    # Deprecated:
    def get(self):
        return self.client.getHelper(self.url)

    # Get file from the data api
    def getFile(self):
        if not self.exists():
            raise Exception('file does not exist - {}'.format(self.path))
        # Make HTTP get request
        response = self.client.getHelper(self.url)
        with tempfile.NamedTemporaryFile(delete = False) as f:
            for block in response.iter_content(1024):
                if not block:
                    break;
                f.write(block)
            f.flush()
            return open(f.name)

    def getName(self):
        _, name = getParentAndBase(self.path)
        return name

    def getBytes(self):
        if not self.exists():
            raise Exception('file does not exist - {}'.format(self.path))
        # Make HTTP get request
        return self.client.getHelper(self.url).content

    def getString(self):
        if not self.exists():
            raise Exception('file does not exist - {}'.format(self.path))
        # Make HTTP get request
        return self.client.getHelper(self.url).text

    def getJson(self):
        if not self.exists():
            raise Exception('file does not exist - {}'.format(self.path))
        # Make HTTP get request
        return self.client.getHelper(self.url).json()

    def exists(self):
        response = self.client.headHelper(self.url)
        return (response.status_code == 200)

    def put(self, data):
        # Post to data api

        # First turn the data to bytes if we can
        if isinstance(data, six.string_types) and not isinstance(data, six.binary_type):
            data = bytes(data.encode())

        if isinstance(data, six.binary_type):
            result = self.client.putHelper(self.url, data)
            if 'error' in result:
                raise Exception(result['error']['message'])
            else:
                return self
        else:
            raise Exception("Must put strings or binary data. Use putJson instead")

    def putJson(self, data):
        # Post to data api
        jsonElement = json.dumps(data)
        result = self.client.putHelper(self.url, jsonElement)
        if 'error' in result:
            raise Exception(result['error']['message'])
        else:
            return self

    def putFile(self, path):
        # Post file to data api
        with open(path, 'rb') as f:
            result = self.client.putHelper(self.url, f)
            if 'error' in result:
                raise Exception(result['error']['message'])
            else:
                return self

    def delete(self):
        # Delete from data api
        result = self.client.deleteHelper(self.url)
        if 'error' in result:
            raise Exception(result['error']['message'])
        else:
            return True
