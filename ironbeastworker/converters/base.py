import logging
import re
import datetime
import socket
import json
import sys
import urllib2
from urlparse import parse_qs



logger = logging.getLogger('convertersLogger')
logging.basicConfig()

LOG_BASE_PATH = r'/storage/logs/'
SEPARATOR = r','
SEPARATOR_REPLACEMENT = r'|'


class Base(object):


    def convert_line(self, line, input_format='json', output_format='dict', to_lower=True, keep_none_string=False):
        res = {}
        parsed_decoded = {}
        prepped_line = {}

        ################### JSON ###############
        if input_format == 'json':
            try:
                if not isinstance(line, dict):
                    prepped_line = json.loads(line)
                else:
                    prepped_line = line

                prepped_line = {key.lower(): value for key, value in prepped_line.iteritems()}

            except:
                logger.exception("Error in base json: line --> %s" % (line))
                
        else:
            prepped_line = {}

        # normalising the values
        res = prepped_line

        # if log is not of installcore:
        #if input_format != 'delimited':
        for field in res:
            try:
                if isinstance(res[field], str):
                    res[field] = self.normalize_value(res[field])

                elif isinstance(res[field], list):
                    fixed_list = []

                    for i, item in enumerate(res[field]):

                        if isinstance(item, dict):

                            item = {key.lower(): value for key, value in item.iteritems()}

                            for key in item:
                                item[key.lower()] = self.normalize_value(item[key])

                            fixed_list.append(item)

                        else:
                            res[field][i] = self.normalize_value(item)

                    res[field] = fixed_list

                # only one level of normalizing:
                # no support for nested json.
                elif isinstance(res[field], dict):
                    res[field] = {self.normalize_value(key): self.normalize_value(value, keep_none_string) for key, value in res[field].iteritems()}
                    try:
                        res[field] = json.dumps(res[field])
                    except:
                        pass
                else:
                    res[field] = self.normalize_value(res[field], keep_none_string)

            except Exception, err:
                logger.exception("convert_line: Cant encode --> %s" % str(err))
                res[field] = ""

        res = dict(res.items() + parsed_decoded.items())
        return res

    def prepare_line_for_copy(self, data):
        try:
            if isinstance(data, list):
                data = [json.dumps(self.fix_unicodes(line), ensure_ascii=False) for line in data]
            else:
                data = json.dumps(self.fix_unicodes(data), ensure_ascii=False)

            print(data)

        except:
            logger.exception("prepare_line_for_copy: Cant json dumps --> %s" % data)
            raise

    def fix_unicodes(self, data):
        return {key: self.normalize_value(data[key]) for key, value in data.iteritems()}

    def normalize_value(self, val, keep_none_string=False):
        if isinstance(val, str) or isinstance(val, unicode):
            val = self.remove_nulls(val)
            for char in val:
                if ord(char) >= 128 or ord(char) < 32:
                    return self.normalize_unicode(val).rstrip()

        if not keep_none_string and val is None:
            return ''

        val = str(val)
        val = val.encode('utf8', errors='ignore')
        return val.rstrip()

    def normalize_unicode(self, val):
        if isinstance(val, str):
            try:
                fixed_unicode = unicode(val, 'UTF-8')
                return fixed_unicode
            except:
                for char in val:
                    if ord(char) >= 128 or ord(char) < 32:
                        #logger.info("normalize unicode fail, removing char: %s with ord: %s from %s"
                        #            % (char, ord(char), val))
                        return self.normalize_unicode(val.replace(char, ' '))

        if isinstance(val, unicode):
            return val

    def remove_nulls(self, val):
        return val.replace('\u0000', ' ').replace('\000', ' ') \
            .replace('\0', ' ').replace('\x00', ' ')


    def remove_non_utf(self, val):

        try:
            val = self.normalize_value(val)

        except Exception as e:
            pass

        finally:
            return re.sub(r'[^(\x20-\x7F)]', '', val)

    def get_country_by_ip(self, ip):
        return "Israel"

    def get_geo_record_by_ip(self, ip):
        return "Tel-Aviv"

    def get_isp_by_ip(self, ip):
        return "Bezeq"

    @staticmethod
    def is_valid_ip(addr):
        try:
            socket.inet_aton(addr)
        except socket.error:
            return False
        return True

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
        except:
            logger.exception("[{2}] Error in {2} validate_varchar ==> {0} ====> Request: {1}".format(sys.exc_info()[0], data, self.__class__.__name__))

        return data

    # Gets an array of fields and changes them from float to smallint
    ## and sets to 0 if out of range
    def validate_smallint(self, data, fields=[]):
        try:
            for field in fields:
                if field in data:
                    val = int(float(data[field]))
                    if val < -32768 or val > 32767:
                        val = 0

                    if val != float(data[field]):
                        data['ib_converter_fix'] = data.get('ib_converter_fix', '') + field + ', '

                    data[field] = val
        except:
            logger.exception("[{2}] Error in {2} validate_smallint ==> {0} ====> Request: {1}".format(sys.exc_info()[0], data, self.__class__.__name__))

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

    # Gets a possible nested property from an object
    def get_by_dot_notation(self, obj, ref):
        val = obj
        for key in ref.split('.'):
            val = val.get(key, None) or val.get(key.lower(), None)
            if (val is None):
                return None
        return val
