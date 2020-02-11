from models.movement_actions import ExerciseAction, UpperBodyStance, LowerBodyStance, Explosiveness
from movement_tags import CardioAction, TrainingType, BodyPosition, Equipment, WeightDistribution
import os
import json
import pandas as pd


class ActionLibraryParser(object):
    def __init__(self):
        self.actions_pd = None
        self.actions = []

    def load_data(self):
        self.actions_pd = pd.read_csv(f'action_library.csv', keep_default_na=False, skiprows=1)

        self.actions = []

        for index, row in self.actions_pd.iterrows():
            action_item = self.parse_row(row)
            if action_item is not None:
                self.actions.append(action_item)

        self.write_actions_json()

    def parse_row(self, row):
        if row['id'] is not None and row['id'] != '':
            action = ExerciseAction(row['id'], row['action'])

            if row.get('training_type') is not None and row['training_type'] != "" and row['training_type'] != "none":
                action.training_type = TrainingType[row['training_type']]
                # if action.training_type == TrainingType.strength_cardiorespiratory:
                #     try:
                #         action.cardio_action = CardioAction[row['cardio_action']]
                #     except KeyError:
                #         print(f"cardio_action: {row['cardio_action']}")
            if row.get('eligible_external_resistance') is not None and row['eligible_external_resistance'] != "":
                row['eligible_external_resistance'].replace(", ", ",")
                resistances = row.get('eligible_external_resistance').split(",")
                try:
                    action.eligible_external_resistance = [Equipment[ex_res] for ex_res in resistances]
                except:
                    print(f"eligible_external_resistance: {row['eligible_external_resistance']}")
            if row.get('stance_lower_body') is not None and row['stance_lower_body'] != "":
                action.lower_body_stance = LowerBodyStance[row['stance_lower_body']]
            if row.get('stance_upper_body') is not None and row['stance_upper_body'] != "":
                action.upper_body_stance = UpperBodyStance[row['stance_upper_body']]
            if row.get('lateral_distribution_pattern') is not None and row['lateral_distribution_pattern'] != "":
                action.lateral_distribution_pattern = WeightDistribution[row['lateral_distribution_pattern']]
            if row.get('percent_bodyweight') is not None and row['percent_bodyweight'] != "":
                action.percent_bodyweight = int(row.get('percent_bodyweight', 0))
            action.lateral_distribution = [0, 0]
            action.apply_resistance = row['apply_resistance'].lower() == "true"
            if row.get('relative_explosiveness') is not None and row['relative_explosiveness'] != "" and row['relative_explosiveness'] != "none":
                action.explosiveness = Explosiveness[row['relative_explosiveness']]
            action.apply_instability = row['apply_instability'].lower() == "true"
            return action
        else:
            return None

    def write_actions_json(self):
        actions_json = {}
        for action in self.actions:
            actions_json[action.id] = action.json_serialise()

        json_string = json.dumps(actions_json, indent=4)
        file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/actions_library.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()


if __name__ == '__main__':
    action_parser = ActionLibraryParser()
    action_parser.load_data()
