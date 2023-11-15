from typing import List
from collections import deque

import openai
from bs4 import BeautifulSoup
from RAI import QAGPT
from reporter import Reporter


class Block_2(Reporter):

    def answers_to_json(self, topic, criterias, answers_from_reporter):
        print("working on answers_to_json")
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

Name of criteria/limit:
[
"The thing": name
"Type": (greater than/less than/equal/null)
"Value": (can be null)
]
"""
        self.answer_check = self.gpt.run(prompt)
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

Name of criteria/limit:
[
"The thing": name
"Type": (greater than/less than/equal/null)
"Value": (can be null)
]

If ther won't be any json-formatted data or if it would be irrelevant - return 'No' to redo the shortening, or return 'Yes' to proceed. So, you're output should only have one word - "Yes" or "No". Do not add any more symbols.
"""
        while True:
            self.answers_to_json(self.topic, self.criteria_str, self.answer_str)
            self.check_the_answer_check = self.gpt.run(prompt)
            print(self.check_the_answer_check)
            if self.check_the_answer_check.find("Yes") != -1:
                return "Yes"
            if self.check_the_answer_check.find("No") != -1:
                return "No"
            print("It doesn't give Yes or No")
