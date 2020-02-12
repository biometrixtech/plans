from models.movement_actions import ExerciseAction, UpperBodyStance, LowerBodyStance, Explosiveness, MuscleAction, PrioritizedJointAction
from movement_tags import CardioAction, TrainingType, Equipment, WeightDistribution
from models.functional_movement_type import FunctionalMovementType
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

            if self.is_valid(row, 'training_type'):
                action.training_type = TrainingType[row['training_type']]
            if self.is_valid(row, 'eligible_external_resistance'):
                row['eligible_external_resistance'] = row['eligible_external_resistance'].replace(", ", ",")
                resistances = row.get('eligible_external_resistance').split(",")
                try:
                    action.eligible_external_resistance = [Equipment[ex_res] for ex_res in resistances]
                except:
                    print(f"eligible_external_resistance: {row['eligible_external_resistance']}")
            if self.is_valid(row, 'stance_lower_body'):
                action.lower_body_stance = LowerBodyStance[row['stance_lower_body']]
            if self.is_valid(row, 'stance_upper_body'):
                action.upper_body_stance = UpperBodyStance[row['stance_upper_body']]
            if self.is_valid(row, 'lateral_distribution_pattern'):
                action.lateral_distribution_pattern = WeightDistribution[row['lateral_distribution_pattern']]
            if self.is_valid(row, 'percent_bodyweight'):
                action.percent_bodyweight = int(row.get('percent_bodyweight', 0))
            if self.is_valid(row, 'lateral_distribution'):
                action.lateral_distribution = [0, 0]
            if self.is_valid(row, 'apply_resistance'):
                action.apply_resistance = row['apply_resistance'].lower() == "true"
            if self.is_valid(row, 'relative_explosiveness'):
                action.explosiveness = Explosiveness[row['relative_explosiveness']]
            if self.is_valid(row, 'apply_instability'):
                action.apply_instability = row['apply_instability'].lower() == "true"

            # primary
            if self.is_valid(row, 'muscle_action'):
                self.primary_muscle_action = MuscleAction[row['muscle_action']]

            action.hip_joint_action = self.get_prioritized_joint_actions(row, 'hip_joint')
            action.knee_joint_action = self.get_prioritized_joint_actions(row, 'knee_joint')
            action.ankle_joint_action = self.get_prioritized_joint_actions(row, 'ankle_joint')
            action.trunk_joint_action = self.get_prioritized_joint_actions(row, 'trunk_joint')
            action.shoulder_scapula_joint_action = self.get_prioritized_joint_actions(row, 'shoulder_scapula_joint')
            action.elbow_joint_action = self.get_prioritized_joint_actions(row, 'elbow_joint')

            # # if self.is_valid(row, 'knee_joint_priority'):
            # #     pass
            # if self.is_valid(row, 'knee_joint_action'):
            #     pass
            # # if self.is_valid(row, 'ankle_joint_priority'):
            # #     pass
            # if self.is_valid(row, 'ankle_joint_action'):
            #     pass
            # # if self.is_valid(row, 'trunk_joint_priority'):
            # #     pass
            # if self.is_valid(row, 'trunk_joint_action'):
            #     pass
            # # if self.is_valid(row, 'shoulder_scapula_joint_priority'):
            # #     pass
            # if self.is_valid(row, 'shoulder_scapula_joint_action'):
            #     pass
            # # if self.is_valid(row, 'elbow_joint_priority'):
            # #     pass
            # if self.is_valid(row, 'elbow_joint_action'):
            #     pass
            # secondary
            if self.is_valid(row, 'muscle_action'):
                pass
            if self.is_valid(row, 'hip_stability'):
                pass
            if self.is_valid(row, 'ankle_stability'):
                pass
            if self.is_valid(row, 'trunk_stability_fm'):
                pass
            if self.is_valid(row, 'pelvis_stability_fm'):
                pass
            if self.is_valid(row, 'shoulder_stability'):
                pass
            if self.is_valid(row, 'elbow_stability'):
                pass
            if self.is_valid(row, 'sij_stability'):
                pass
            return action
        else:
            return None

    def get_prioritized_joint_actions(self, row, joint):
        if self.is_valid(row, f'{joint}_action'):
            joint_priority = 0
            if self.is_valid(row, f'{joint}_priority'):
                joint_priority = int(row[f'{joint}_priority'])
            joint_actions = row[f'{joint}_action']
            joint_actions = joint_actions.replace(", ", ",")
            joint_actions = joint_actions.replace(" ", "_")
            joint_actions = joint_actions.lower().split(",")
            try:
                return [PrioritizedJointAction(joint_priority, FunctionalMovementType[j_action]) for j_action in joint_actions]
            except:
                print(joint_actions)
        return []


    @staticmethod
    def is_valid(row, name):
        if row.get(name) is not None and row[name] != "" and row[name] != "none":
            return True
        return False



    def write_actions_json(self):
        actions_json = {}
        for action in self.actions:
            actions_json[action.id] = action.json_serialise(initial_read=True)

        json_string = json.dumps(actions_json, indent=4)
        file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/actions_library.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()


if __name__ == '__main__':
    action_parser = ActionLibraryParser()
    action_parser.load_data()
