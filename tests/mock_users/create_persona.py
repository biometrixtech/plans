import os
import time
from aws_xray_sdk.core import xray_recorder
os.environ['ENVIRONMENT'] = 'dev'
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

from persona import Persona
from soreness_history import create_body_part_history, persistent2_question, acute_pain_no_question

def create_persona_with_two_historic_soreness(days):
    soreness_history = []
    right_knee_persistent2_question = create_body_part_history(persistent2_question(), 7, 2, True)
    soreness_history.append(right_knee_persistent2_question)
    left_knee_acute_pain_no_question = create_body_part_history(acute_pain_no_question(), 7, 1, True)
    soreness_history.append(left_knee_acute_pain_no_question)
    persona1 = Persona('d2ad1be7-18ba-4126-9fc3-047c37a60018')
    persona1.soreness_history = soreness_history
    persona1.create_history(days=days)


if __name__ == '__main__':
    start = time.time()
    history_length = 35
    create_persona_with_two_historic_soreness(history_length)
    print(time.time() - start)
#    update_metrics(user_id, event_date)