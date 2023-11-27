from typing import List
import os
import json

import openai
from bs4 import BeautifulSoup
from RAI import QAGPT
from reporter import Reporter


class Block_2(Reporter):


    def find_subkeys(self, list, index):
        type_value = ""
        value_value = ""
        for i in range(index, len(list)):
            print(i)
            print(list[i])
            if type_value != "" and value_value != "":
                break
            if "Type" in list[i]:
                if "{" in list[i]:
                    while True:
                        print(i)
                        print(list[i])
                        print(type_value)
                        type_value = list[i+1]
                        if "}" in list[i]:
                            type_value += list[i].remove('}').remove('{')
                            break
                else:
                    type_value = list[i]
                continue
            elif "Value" in list[i]:
                if "{" in list[i]:
                    while True:
                        print (value_value)
                        try:
                            value_value = list[i+1]
                            i += 1
                            if "}" in list[i+1]:
                                value_value += list[i+1].remove('}')
                                break
                        except:
                            break
                else:
                    value_value = list[i]
                continue
        type_value = type_value.replace('"', '')
        value_value = value_value.replace('"', '')
        type_value = type_value.replace('"', '')
        value_value = value_value.replace('"', '')
        if type_value[-1] == ",":
            type_value = type_value[:-1]
        if value_value[-1] == ",":
            value_value = value_value[:-1]
        type_value = type_value.replace('Type: ', "")
        value_value = value_value.replace('Value: ', "")
        return type_value, value_value


    def parse_answer_json(self):
        final_dict = {}
        debug_data = self.answer_check
        list_strings = debug_data.split('\n')
        print('\n\n\nLets start with parsing\n\n\n')
        for i in range(0, len(list_strings)):
            print("list_strings[i]", list_strings[i])
            try:
                if "Name of criteria/limit" in list_strings[i] or "{" == list_strings[i+1] and list_strings[i] != "[":
                    if "}" not in list_strings[i]:
                        header_string = list_strings[i]
                    if "Name of criteria/limit" in list_strings[i]:
                        print("Name of criteria/limit", "in that thing")
                        header_string = list_strings[i].replace('Name of criteria/limit:', '')
                    print("header_string", header_string)
                    header_string = list_strings[i].replace(',', '')
                    header_string = header_string.replace('"', '')
                    if header_string[-1] == " " and header_string[-2] == ":":
                        header_string = header_string[:-2]
                    type_value, value_value = self.find_subkeys(list_strings, i+1)
                    print("type_value, value_value", type_value, value_value)
                    final_dict[header_string] = {"Type": type_value, "Value": value_value}
                    print("final_dict in for", final_dict)
            except:
                print("except")
            print("final_dict", final_dict)
        return final_dict

    def save_answer_json(self):
        self.path_to_json = f"assets/saved_answer.json"
        # print("self.answer_str, self.answer_check", self.answer_str, self.answer_check)
        data_dict = self.parse_answer_json()
        print("data_dict", data_dict)
        try:
            with open(self.path_to_json, 'w') as outfile:
                json.dump(data_dict, outfile)
        except FileNotFoundError:
            directory = os.path.dirname(self.path_to_json)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(self.path_to_json, 'w') as outfile:
                json.dump(data_dict, outfile)
        return data_dict


    def answers_to_json(self, topic, criterias, answers_from_reporter):
        # print("working on answers_to_json")
        self.criteria_str = "\n".join(criterias)
        self.answer_str = "\n".join(f"{i}. {a}" for i, a in enumerate(answers_from_reporter, 1))
        self.topic = topic
        prompt = f"""
Consider the topic below:
<TOPIC>
{self.topic}
</TOPIC>

Consider the list of criterias for the user answer:
<CRITERIAS>
{self.criteria_str}
</CRITERIAS>

Consider user's answers:
<ANSWER>
{self.answer_str}
</ANSWER>

Turn user-supplied information into json format.

The template is as follows:
The thing - should be about what to change. Name of it
Type - should be about, what kind of change user wants. "greater than" to increase the thing, "less than" to decrease the thing, "equal" to have value set to the thing, but not relating for any existing somthing, "null" in case you can't come up with understanding, which flag to use
Value - should be about any counteble data of the thing in change. For example, how much of the thing user wants. It can be null if there not any

Be sure to strictly mainain the following pattern, it's important.

"Name of criteria/limit:" - The thing [
"Type": (greater than/less than/equal/null)
"Value": (can be null)
]

"""
        self.answer_check = self.gpt.run(prompt)
        # print("self.answer_check", self.answer_check)
        return self.answer_check
    
    def check_answer_check(self):
        prompt = f"""
Consider the topic below:
<TOPIC>
{self.topic}
</TOPIC>

Consider the list of criterias for the user answer:
<CRITERIAS>
{self.criteria_str}
</CRITERIAS>

Consider user's answers:
<ANSWER>
{self.answer_str}
</ANSWER>

Check shortened information:
<INFO>
{self.answer_check}
</INFO>

How to check:

Format of the INFO should be as following:

The thing - should be about what to change. Name of it
Type - should be about, what kind of change user wants. "greater than" to increase the thing, "less than" to decrease the thing, "equal" to have value set to the thing, but not relating for any existing somthing, "null" in case you can't come up with understanding, which flag to use
Value - should be about any counteble data of the thing in change. For example, how much of the thing user wants. It can be null if there not any

"Name of criteria/limit: - The thing" [
"Type": (greater than/less than/equal/null)
"Value": (can be null)
]

If there won't be any json-formatted data or if it would be irrelevant - return 'No' to redo the shortening, or return 'Yes' to proceed. So, you're output should only have one word - "Yes" or "No". Do not add any more symbols.
"""
        while True:
            # print("self.answer_str-1", self.answer_str)
            # print("self.answer_check-1", self.answer_check)
            self.check_the_answer_check = self.gpt.run(prompt)
            # print("self.answer_check-2", self.answer_check)
            # print("self.check_the_answer_check", self.check_the_answer_check)
            # print("self.answer_str-2", self.answer_str)
            if self.check_the_answer_check.find("Yes") != -1:
                return "Yes"
            if self.check_the_answer_check.find("No") != -1:
                self.answers_to_json(self.topic, self.criteria_str, self.answer_str)
                print("No")
                continue
            print("It doesn't give Yes or No")

