from typing import List
from collections import deque

import openai
from bs4 import BeautifulSoup
from RAI import QAGPT


class Reporter:
    
    def __init__(self, **kwargs):
        # GPT attributes
        self.model = kwargs.get("model", None)
        self.temperature = kwargs.get("temperature", 0)
        self.gpt = QAGPT(model=self.model, temperature=self.temperature, key = 'xx-xxxxx')
        self.n_retries = kwargs.get("n_retries", 5)
        # Q/A flow attributes
        self.topic = None
        self.criterias = None
        self._maxlen = 5
        self.questions = deque(maxlen=self._maxlen)
        self.answers = deque(maxlen=self._maxlen)
        self._raw_questions = deque(maxlen=self._maxlen)
        self.verdict = False
        return
    
    
    def get_question_prompt(self, topic: str, criterias: List[str]) -> str:
        criteria_str = "\n".join(criterias)
        prompt = f"""
Consider the topic below:
<TOPIC>
{topic}
</TOPIC>

Consider the list of criterias for the user answer:
<CRITERIAS>
{criteria_str}
</CRITERIAS>

Take a deep breath and think step-by step about the specific question,
that would retrieve information, specified in <TOPIC> section from the user,
so that the answer will follow the criterias, specified in <CRITERIAS> section.
Put your thinking process inside of <THINKING> section.

After you finish thinking write the question, according to the task above. 
Put your question in <QUESTION> section.

Provide your answer (except for sections' names) in Russian Language. 
"""
        return prompt
    
    
    def _get_question(self) -> str:
        prompt = self.get_question_prompt(self.topic, self.criterias)
        raw_question = self.gpt.run(prompt)
        return raw_question
    
    
    def _parse_raw_question(self, raw_question: str) -> str:
        soup = BeautifulSoup(raw_question, "html.parser")
        q_tag = soup.find("question")
        if not q_tag:
            raise ValueError("<QUESTION> tag not found in model answer.")
        question = q_tag.get_text()
        return question
    
    
    def get_question(self, topic: str, criterias: List[str]) -> str:
        self.topic = topic
        self.criterias = criterias
        for i in range(self.n_retries):
            try:
                raw_question = self._get_question()
                self._raw_questions.append(raw_question)
                question = self._parse_raw_question(raw_question)
                self.questions.append(question)
                return question
            except Exception:
                print(f"[ERROR]: Failed to fetch question for user. Exception: {e}")
        raise ValueError(f"Unable to obtain question after {self.n_retries} retries.")
        
        
    def get_answer(self) -> str:
        answer = input("[User]: ")
        self.answers.append(answer)
        return answer
    
    # Debug
    def get_answer_from_list(self, from_list_answers) -> str:
        answer = from_list_answers
        self.answers.append(answer)
        return answer
    
    def get_followup_prompt(
        self,
        questions: List[str],
        criterias: List[str],
        answers: List[str]
    ) -> str:
        question_str = "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1))
        criteria_str = "\n".join(criterias)
        answer_str = "\n".join(f"{i}. {a}" for i, a in enumerate(answers, 1))
        prompt = f"""
Consider the questions below:
<QUESTION>
{question_str}
</QUESTION>

Consider the list of criterias for the user answer:
<CRITERIAS>
{criteria_str}
</CRITERIAS>

Consider user's answers:
<ANSWER>
{answer_str}
</ANSWER>

Take a deep breath and think step-by step whether user's answer, 
provided in <ANSWER> section, fullfills all the requirements, presented in <CRITERIAS> section.
Put your thinking process inside of <THINKING> section.

After you finish thinking write your verdict, whether the answer fulfills the requirements or not. The answer should be either "YES" or "NO".
Put your verdict in <VERDICT> section.

If your verdict is "NO", provide follow-up question, which aims to obtain missing information.
Put your foolow-up question in <FOLLOWUP> section.
If your verdict is "YES" do not write "FOLLOWUP" section.

Provide your answer (except for sections' names) in Russian Language. 
"""
        return prompt
    
    
    def _get_followup(self) -> str:
        print(self.questions)
        print(self.answers)
        prompt = self.get_followup_prompt(self.questions, self.criterias, self.answers)
        raw_followup = self.gpt.run(prompt)
        return raw_followup
    
    
    def _parse_raw_followup(self, raw_followup: str) -> str:
        soup = BeautifulSoup(raw_followup, "html.parser")
        v_tag = soup.find("verdict")
        if not v_tag:
            raise ValueError("<VERDICT> tag not found in model answer.")
        verdict = v_tag.get_text().strip().lower()
        if verdict == "yes":
            self.verdict = True
            return None
        f_tag = soup.find("followup")
        if not f_tag:
            raise ValueError("<FOLLOWUP> tag not found in model answer.")
        followup = f_tag.get_text()
        return followup
    
    
    def get_followup(self) -> str:
        for i in range(self.n_retries):
            try:
                raw_followup = self._get_followup()
                self._raw_questions.append(raw_followup)
                followup = self._parse_raw_followup(raw_followup)
                self.questions.append(followup)
                return followup
            except Exception as e:
                print(f"[ERROR]: Failed to fetch follow-up question for user. Exception: {e}")
        raise ValueError(f"Unable to obtain follow-up question after {self.n_retries} retries.")
        
    
    def display_question(self) -> None:
        if not self.questions:
            return
        print(f"[Reporter]: {self.questions[-1]}")
        return
        
    
    def run(self, topic: str, criterias: List[str]) -> None:
        self.get_question(topic, criterias)
        while not self.verdict:
            question = self.display_question()
            answer = self.get_answer()
            if not answer:
                break
            followup = self.get_followup()
        print("Discussion completed") # Remove this later; for debug purposes only
        return
    
    def runy(self, topic: str, criterias: List[str], list_answers) -> None:
        self.get_question(topic, criterias)
        i = 0
        # print(len(list_answers[i]))
        while not self.verdict:
            print(i)
            question = self.display_question()
            print("list_answers[i]", list_answers[i])
            answer = self.get_answer_from_list(list_answers[i])
            i += 1
            print("Hmm")
            if i>=len(list_answers):
                break
            if not answer:
                break
            followup = self.get_followup()
        print("Discussion completed") # Remove this later; for debug purposes only
        return
    

    def __call__(self, *args, **kwargs) -> None:
        return self.run(*args, **kwargs)