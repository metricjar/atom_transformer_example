import json

class Base(object):

    def convert_line(self, line):
        try:
            line = json.loads(line)
            print("Working on line {}".format(line))
        except:
            print("Malformed json {}".format(line))
            exit(1)
        return {key.lower(): value for key, value in line.iteritems()}

    def enrich(self, request, data):
        data['ib_city'] = self.get_geo_record_by_ip(request['ip'])
        data['ib_country'] = self.get_country_by_ip(request['ip'])
        data['ib_isp'] = self.get_isp_by_ip(request['ip'])
        data['ib_datetime_utc'] = request['datetime']

    def prepare_line_for_copy(self, data):
        # our transformer will remove bad characters.
        print("Result: {}".format(json.dumps(data)))

    def get_country_by_ip(self, ip):
        return "Israel"

    def get_geo_record_by_ip(self, ip):
        return "Tel-Aviv"

    def get_isp_by_ip(self, ip):
        return "Bezeq"

    # Gets a map of { field_name: length } and cuts the value to that size
    def validate_varchar(self, data, validations):
        try:
            for key, limit in validations.iteritems():
                if key in data:
                    value = data[key]
                    if isinstance(value, str) or isinstance(value, unicode):
                        if len(value.encode('utf-8')) > limit:
                            data['ib_converter_fix'] = data.get('ib_converter_fix', '') + key + ', '
                            data[key] = value.encode('utf-8')[:limit]
        except Exception as e:
            print("Error validating varchar: {}".format(e))
            exit(2)

        return data

    # Gets a map of { old_name: new_name } and changes it from old to new
    def rename_keys(self, data, mapping):
        for old, new in mapping.iteritems():
            self.rename_key(data, old, new)

    # Gets the row and old_name, new_name and renames old to new
    def rename_key(self, data, old, new):
        if data.get(old):
            data[new] = data[old]
            del data[old]