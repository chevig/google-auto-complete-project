import json
from offline import simplify_word
from auto_complete_data import AutoCompleteData
from string import ascii_lowercase


def merge_two(l1, l2):
    if not l1:
        return l2

    elif not l2:
        return l1

    elif l1[0].score < l2[0].score:
        return [l2[0]] + merge_two(l1, l2[1:])

    else:
        return [l1[0]] + merge_two(l1[1:], l2)


def merge_three(l1, l2, l3):
    return merge_two(merge_two(l1, l2), l3)


def calculate_omit_add_score(prefix_len, index):
    score = {1: 10, 2: 8, 3: 6, 4: 4}
    try:
        return 2 * prefix_len - score[index]
    except:
        return 2 * prefix_len - 2


def calculate_replace_score(prefix_len, index):
    score = {1: 5, 2: 4, 3: 3, 4: 2}
    try:
        return 2 * prefix_len - score[index]
    except:
        return 2 * prefix_len - 1


def omit_character(data_dict, prefix, length, completion_list):
    reversed_prefix = prefix[::-1]
    list = []
    no_dup_list = [[x.source_text, x.offset] for x in completion_list]

    for i in range(len(prefix)):
        try:
            path_list = data_dict[(reversed_prefix[:i] + reversed_prefix[i + 1:])[::-1]]
            score = calculate_omit_add_score(len(prefix) - 1, len(prefix) - i)

            for sentence in path_list:

                if [sentence[0], sentence[1]] not in no_dup_list:
                    list.append(AutoCompleteData(sentence[0], sentence[1], score))
                    no_dup_list.append([sentence[0], sentence[1]])

                    if len(list) == length:
                        return list
        except:
            continue
    return list


def add_character(data_dict, prefix, length, completion_list):
    reversed_prefix = prefix[::-1]
    list = []
    no_dup_list = [[x.source_text, x.offset] for x in completion_list]

    for i in range(len(prefix)):
        for char in ascii_lowercase:
            try:
                path_list = data_dict[(reversed_prefix[:i] + char + reversed_prefix[i:])[::-1]]
                score = calculate_omit_add_score(len(prefix), len(prefix) - i + 1)

                for sentence in path_list:
                    if [sentence[0], sentence[1]] not in no_dup_list:  # TODO check also line
                        list.append(AutoCompleteData(sentence[0], sentence[1], score))
                        no_dup_list.append([sentence[0], sentence[1]])

                        if len(list) == length:
                            return list
            except:
                continue
    return list


def replace_character(data_dict, prefix, length, completion_list):
    reversed_prefix = prefix[::-1]
    list = []
    no_dup_list = [[x.source_text, x.offset] for x in completion_list]
    for i in range(len(prefix)):
        for char in ascii_lowercase:
            try:
                path_list = data_dict[(reversed_prefix[:i] + char + reversed_prefix[i + 1:])[::-1]]
                score = calculate_replace_score(len(prefix) - 1, len(prefix) - i)

                for sentence in path_list:
                    if [sentence[0], sentence[1]] not in no_dup_list:
                        list.append(AutoCompleteData(sentence[0], sentence[1], score))
                        no_dup_list.append([sentence[0], sentence[1]])

                        if len(list) == length:
                            return list
            except:
                continue
    return list


def find_similar_matches(data_dict, prefix, length, completion_list):
    list = []
    list1 = omit_character(data_dict, prefix, length, completion_list)
    list2 = add_character(data_dict, prefix, length, completion_list)
    list3 = replace_character(data_dict, prefix, length, completion_list)
    list = merge_three(list1, list2, list3)
    list_length = len(list) - 1
    no_dup_list = [[x.source_text, x.offset] for x in list][::-1]

    for i, obj in enumerate(no_dup_list):

        if no_dup_list.count(obj) > 1:
            list.pop(list_length - i)
            no_dup_list[i] = []

    return list[:length] if len(list) >= length else list


def find_identical_matches(data, prefix):
    my_list = []

    for sentence in data:
        my_list.append(AutoCompleteData(sentence[0], sentence[1], len(prefix) * 2))

    return my_list


def find_completions(data_dict, prefix):
    completion_list = []
    prefix = simplify_word(prefix)[:10] if len(prefix) > 10 else simplify_word(prefix)

    try:
        completion_list = find_identical_matches(data_dict[prefix], prefix)
    except:
        return find_similar_matches(data_dict, prefix, 5, completion_list)

    length = len(completion_list)

    if length < 5:
        completion_list += find_similar_matches(data_dict, prefix, 5 - length, completion_list)

    return completion_list


def get_best_5_completions(prefix: str):
    with open('offline_data.json', 'r') as file:
        data_dict = json.load(file)

    return find_completions(data_dict, prefix)


def print_results(best_completions):
    if len(best_completions) > 0:
        print(f"Here {len(best_completions)} suggestions:")
    else:
        print("Oops, no matching results...")

        return

    for index, completion in enumerate(best_completions, 1):
        print(
            f"{index}. {completion.completed_sentence} ({completion.source_text} {completion.offset}) score: ({completion.score})")


def auto_completion():
    npt = ""
    print("Enter your text <'#' to exit>:")
    while True:
        npt = npt + input(npt)
        if npt[-1] == '#':
            break
        print_results(get_best_5_completions(npt))
