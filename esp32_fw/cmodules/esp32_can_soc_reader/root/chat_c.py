
def make_string():
    out_string = ""
    separator = ","

    counter = 0
    while counter < 10:
        out_string += str(counter)
        out_string += separator
        counter += 1
    return out_string

response = make_string()
print(response)
