import json
import os
from string import punctuation


def simplify_word(word):

    return " ".join("".join(char for char in word if char not in punctuation).lower().split())


def get_all_substrings_of_length_till_10(string):

    return set([string[i: j] for i in range(len(string)) for j in range(i + 1, min(i + 11, len(string) + 1))]) - set(
        ' ')


def get_line(path, line):
    with open(path) as file:

        return file.read().split("\n")[line - 1]


def create_json(data):
    with open('offline_data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4, sort_keys=True)


def store_data(data_dic, file_path, line_in_file, line, substrings):
    for string in substrings:

        if string not in data_dic.keys():
            data_dic[string] = []
        data_dic[string].append([file_path, line_in_file, line.find(string)]) if len(
            data_dic[string]) < 5 else line.find(string) > data_dic[string][4][2]
        data_dic[string].sort(key=lambda x: x[2])


def read_line_by_line(data_dic, file_path, lines):
    for line_in_file, line_string in enumerate(lines, 1):

        if line_string != '':
            line_string = simplify_word(line_string)
            substrings = get_all_substrings_of_length_till_10(line_string)

            store_data(data_dic, file_path, line_in_file, line_string, substrings)


def read_single_file(data_dic, file_path):
    with open(file_path, encoding="utf8") as file:
        lines = file.read().split("\n")
        read_line_by_line(data_dic, file_path, lines)


def read_all_files(my_dic, root_directory):
    for subdir, dirs, files in os.walk(root_directory):
        for file in files:
            read_single_file(my_dic, os.path.join(subdir, file))


def create_dict_offline():
    print("Loading the files and preparing the system...")
    my_dict = {}
    read_all_files(my_dict, "Sample_text/")
    create_json(my_dict)
    print("The system is ready.")
