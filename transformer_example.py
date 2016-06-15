import sys
from atom_transformer_dev.base import Base


class Test(Base):

    def handle_line(self, request):
        """
        :param request: string - stringified json.
        :param input_format: string
        :param output_format: string
        :return: dict
        """
        # Send your data json to the convert line method.
        data = self.convert_line(request['data'])

        # This is an example of using enrichment from the base class.
        self.enrich(request, data)

        # Validation of column's length
        self.validate_varchar(data, {"a": 2})

        # Example of using keys renaming
        self.rename_keys(data, {"d": "f"})

        # TODO: Continue to transform your event here

        # Return the line after the transformation
        return self.prepare_line_for_copy(data)


if __name__ == "__main__":
    try:
        print("Working on file {}".format(sys.argv[1]))
    except:
        print("Please supply a filename with events as an argument")
        exit(2)
    # Initialize the Test class
    a = Test()

    # Request mock - stringified json with a json 'data' field
    mockReq = {"datetime": "10003210", "ip": "10.0.0.0", "data": '{"a": "abc", "b": "c"}'}
    with open (sys.argv[1]) as f:
        for line in f:
            if line:
                mockReq['data'] = line
                # print the converted results.
                a.handle_line(mockReq)