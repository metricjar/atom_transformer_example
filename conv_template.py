from ironbeastworker.converters.base import Base
import json


class Test(Base):

    def handle_line(self, request, input_format='json', output_format='dict'):
        """
        :param request: string - stringified json.
        :param input_format: string
        :param output_format: string
        :return: dict
        """
        # Send your data json to the convert line method.
        converted = self.convert_line(request['data'], input_format, output_format)
        # Perform any modifications that you wish to your data
        converted['ip'] = request['ip']
        # Return the line after conversion
        return self.prepare_line_for_copy(converted)


if __name__ == "__main__":
    # Initialize the Test class
    a = Test()

    # Request mock - stringified json with a json 'data' field
    mockReq = '{"datetime": "10003210", "ip": "10.0.0.0", "data": {"a": "b", "b": "c"}}'

    # print the converted results.
    a.handle_line(json.loads(mockReq))