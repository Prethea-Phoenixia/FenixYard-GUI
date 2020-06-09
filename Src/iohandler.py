import os

# return a list of the .name attribute of a list of instances, in order.
def index_name(stuffs):
    stuff_index = []
    for stuff in stuffs:
        stuff_index.append(stuff.name)
    return stuff_index


# try to return the parent_clas instance having the .name attr of input string.
# will attempt splicing if possible.
def bind_str_to_inst(input_string, parent_ls):
    # bypass string when no parent_clas given
    if parent_ls == []:
        return input_string

    string_list = input_string.split("|")
    parent_index = index_name(parent_ls)
    return_list = []
    for string in string_list:
        if string not in parent_index:
            # falls back to string mode
            return input_string
        s_pos = parent_index.index(string)
        return_list.append(parent_ls[s_pos])
    return return_list


def return_instance_from_list(input_string, list_of_stuff):
    index_of_stuff = index_name(list_of_stuff)
    place = index_of_stuff.index(input_string)
    return list_of_stuff[place]


# reads txt file, creates and return list of objects of the given class
# with attributes set according to the csv header and value
# txt header must have same name as class attributes
# if value matches that of parent_insance, return that instead.
# call additional calls at the end. string list.
def readtxt(filename, clas, parent_ls=[], additional_calls=None):
    def sanitize_str(myString):
        removal_list = ["\t", "\n"]
        for s in removal_list:
            myString = myString.replace(s, "")
        return myString

    with open(filename) as f:
        is_first_row = True
        headers = []
        stuffs = []
        for line in f:
            line_ls_str = line.split(",")
            if is_first_row:
                for head in line_ls_str:
                    headers.append(sanitize_str(head))
                is_first_row = False
            else:
                new_stuff = clas()
                values = line_ls_str
                i = 0
                for attr in headers:
                    try:
                        setattr(new_stuff, attr, float(values[i]))
                    except ValueError:
                        setattr(
                            new_stuff,
                            attr,
                            bind_str_to_inst(sanitize_str(values[i]), parent_ls),
                        )
                    i += 1
                stuffs.append(new_stuff)

        for stuff in stuffs:
            if additional_calls is not None:
                for call in additional_calls:
                    getattr(stuff, call)()
        return stuffs


# return a dictionary of all files
def all_file_with_extension(
    file_extension, path=os.path.dirname(os.path.realpath(__file__))
):
    result = [each for each in os.listdir(path) if each.endswith(file_extension)]
    return result

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(all_file_with_extension(".py", dir_path))
    a = all_file_with_extension(".py", dir_path)
    with open(a[0]) as f:
        data = f.readlines()
        for line in data:
            print(line)
