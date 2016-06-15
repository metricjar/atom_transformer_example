import json

class Base(object):

    def convert_line(self, data):
        """
        We assume that your events are in valid json format
        :param data: valid json format string
        :return: dict with keys in lower case.
        """
        try:
            data = json.loads(data)
            print("Working on line {}".format(data))
        except:
            print("Malformed json {}".format(data))
            exit(1)

        return {key.lower(): value for key, value in data.iteritems()}

    def enrich(self, request, data):
        """
        Will enrich the event with our custom enrichment capabilities.
        It is not required to add all of them.
        :param request: the request
        :param data:
        :return:
        """
        data['ib_datetime_utc'] = request['datetime']
        data['ib_ip'] = request['ip']

        # This is a mock enrichment
        enrichment = self.getDataFromIPorUA()

        data['ib_cc'] = enrichment['cc']
        data['ib_city'] = enrichment['city']
        data['ib_zip'] = enrichment['zip']
        data['ib_isp'] = enrichment['isp']
        data['ib_region'] = enrichment['region']
        data['ib_os'] = enrichment['os']
        data['ib_os_ver'] = enrichment['ib_os_ver']
        data['ib_os_full_ver'] = enrichment['ib_os_full_ver']
        data['ib_device'] = enrichment['ib_device']
        data['ib_device_type'] = enrichment['ib_device_type']
        data['ib_browser'] = enrichment['ib_browser']
        data['ib_browser_ver'] = enrichment['ib_browser_ver']
        data['ib_browser_full_ver'] = enrichment['ib_browser_full_ver']

    def prepare_line_for_copy(self, data):
        # our transformer will remove bad characters here
        print("Result: {}".format(json.dumps(data)))

    def getDataFromIPorUA(self):
        """
        A mock enrichment for this example purpose
        :return:
        """
        return {
            'cc': 'IL',
            'city': 'TLV',
            'zip': '90210',
            'isp': 'Bezeq',
            'region': '',
            'os': 'Windows',
            'ib_os_ver': '10',
            'ib_os_full_ver': '10.0.1',
            'ib_device': 'PC',
            'ib_device_type': '',
            'ib_browser': 'IE',
            'ib_browser_ver': '11',
            'ib_browser_full_ver': '11.0.1'
        }

    def validate_varchar(self, data, validations):
        """
        Will cut the lengths of long varchars according to the validation param
        :param data: dict
        :param validations: dict of { field_name: length }
        :return:
        """
        try:
            for key, limit in validations.iteritems():
                if key in data:
                    value = data[key]
                    if isinstance(value, str) or isinstance(value, unicode):
                        if len(value.encode('utf-8')) > limit:
                            # We will save the fields we cut in the ib_converter_fix field
                            data['ib_converter_fix'] = data.get('ib_converter_fix', '') + key + ', '
                            data[key] = value.encode('utf-8')[:limit]
        except Exception as e:
            print("Error validating varchar: {}".format(e))
            exit(2)

        return data

    def rename_keys(self, data, mapping):
        """
        change the field names according to the mapping param
        :param data: dict
        :param mapping: dict of { old_name: new_name }
        :return:
        """
        for old, new in mapping.iteritems():
            self.rename_key(data, old, new)

    def rename_key(self, data, old, new):
        """
        Replace a key with a new name.
        :param data: dict
        :param old: string
        :param new: string
        :return:
        """
        if data.get(old):
            data[new] = data[old]
            del data[old]