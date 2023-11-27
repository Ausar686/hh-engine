import json

from reporter import Reporter
from block_2 import Block_2

# model = "gpt-4-1106-preview"
model = "gpt-4"
# model = "gpt-3.5-turbo-1106"
# model = "gpt-3.5-turbo"

reporter = Reporter(model=model)
block_2 = Block_2(model = model)

topic = "Планы по финансовому развитию"
criterias = [
    "Указание конкретных  диапазонов доходов спустя конкретный промежуток времени"
]

list_of_debug_answers = ['Зарплата 10000-15000 долларов в месяц, планирую устроиться в Google, а для этого - подготовиться к собеседованиям с помощью LeetCode', 'Хочу линейно увеличивать зарплату в течение 5 лет с 3 до 10-15 тысяч долларов. Т.е. хочу увеличивать зарплату на 2-3 тысячи долларов в месяц ежегодно. Для этого хочу изучать более углубленно программирование и развивать управленческие навыки', '10-15 тысяч хочу через 5 лет. Промежуточные цели: 5 тысяч через год, 7 тысяч - через 2, 9 тысяч - через 3 и так далее' 
]

reporter.runy(topic, criterias, list_of_debug_answers)

reporter._raw_questions

print(reporter.answers)

print(block_2.answers_to_json(reporter.topic, reporter.criterias, reporter.answers))

while True:
    print("block_2.check_answer_check")
    if block_2.check_answer_check() == "Yes":
        print(block_2.save_answer_json())
        break
    else:
        print(block_2.answer_check)