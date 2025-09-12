import pprint

data = {
    'name': 'Alice',
    'age': 30,
    'city': 'New York',
    'hobbies': ['reading', 'hiking', 'coding'],
    'details': {
        'occupation': 'Engineer',
        'company': 'Tech Corp'
    }
}

# Get the pretty-printed string
print("print data")
print(data)
print("pprint.pprint(data)")
pprint.pprint(data)
print("pprint.pformat(data)")
formatted_data_string = pprint.pformat(data)
print(formatted_data_string)

print("Write pretty-printed data to output.txt using pformat()")
# Write the string to a file
with open('output.txt', 'w') as f:
    f.write(formatted_data_string)

info = {
    'name': 'Bob',
    'age': 25,
    'city': 'London',
    'hobbies': ['painting', 'gaming'],
    'details': {
        'occupation': 'Designer',
        'company': 'Creative Studio'
    }
}

# Open the file in write mode
with open('output_stream.txt', 'w') as outfile:
    # Create a PrettyPrinter instance with the file as the stream
    pp = pprint.PrettyPrinter(indent=4, stream=outfile)
    # Pretty-print the data directly to the file
    pp.pprint(info)

print("Pretty-printed data written to output_stream.txt using PrettyPrinter with stream.")