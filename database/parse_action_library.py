from models.movement_actions import ExerciseAction, UpperBodyStance, LowerBodyStance, Explosiveness, MuscleAction, PrioritizedJointAction, MovementSpeed, MovementResistance
from movement_tags import TrainingType, Equipment, WeightDistribution, BodyPosition
from models.functional_movement_type import FunctionalMovementType
import os
import json
import pandas as pd


class ActionLibraryParser(object):
    def __init__(self):
        self.actions_pd = None
        self.actions = []

    def load_data(self, files):
        """

        :param files: prioritized ordered list of file suffix.
                      If the same action occurs in second file as the first one, data from first file will be discarded
        :return:
        """
        actions_json = {}
        for file in files:
            self.actions_pd = pd.read_csv(f'action_library{file}.csv', keep_default_na=False, skiprows=1)

            self.actions = []

            for index, row in self.actions_pd.iterrows():
                action_item = self.parse_row(row)
                if action_item is not None:
                    self.actions.append(action_item)
            actions_json_file = self.get_actions_json()
            actions_json.update(actions_json_file)

        self.write_actions_json(actions_json)

    def parse_row(self, row):
        if row['id'] is not None and row['id'] != '':
            action = ExerciseAction(row['id'], row['action_name'])

            if self.is_valid(row, 'training_type'):
                try:
                    action.training_type = TrainingType[row['training_type']]
                except:
                    return None
            # TODO: Read in categorization as well
            if self.is_valid(row, 'eligible_external_resistance'):
                row['eligible_external_resistance'] = row['eligible_external_resistance'].replace(", ", ",")
                resistances = row.get('eligible_external_resistance').lower().split(",")
                try:
                    action.eligible_external_resistance = [Equipment[ex_res] for ex_res in resistances]
                except:
                    print(f"eligible_external_resistance: {row['eligible_external_resistance']}")
            if self.is_valid(row, 'stance_lower_body'):
                action.lower_body_stance = LowerBodyStance[row['stance_lower_body']]
            if self.is_valid(row, 'stance_upper_body'):
                action.upper_body_stance = UpperBodyStance[row['stance_upper_body']]

            if self.is_valid(row, 'body_position'):
                action.body_position = BodyPosition[row['body_position']]
            # TODO: Remove this once importing from all new sheets that have body_position defined
            elif action.lower_body_stance is not None:
                if action.lower_body_stance == LowerBodyStance.single_leg:
                    action.body_position = BodyPosition.single_leg_moving
                elif action.lower_body_stance == LowerBodyStance.double_leg:
                    action.body_position = BodyPosition.double_leg_moving

            if self.is_valid(row, 'lateral_distribution_pattern'):
                action.lateral_distribution_pattern = WeightDistribution[row['lateral_distribution_pattern']]
            if self.is_valid(row, 'percent_bodyweight'):
                action.percent_bodyweight = int(float(row.get('percent_bodyweight', 0)))
            if self.is_valid(row, 'lateral_distribution'):
                lateral_distribution = row['lateral_distribution'].split(',')
                try:
                    lateral_distribution = [int(float(val.strip())) for val in lateral_distribution]
                except ValueError:
                    print(lateral_distribution)
                else:
                    if len(lateral_distribution) == 0:
                        action.lateral_distribution = [50, 50]
                    elif len(lateral_distribution) == 1:
                        action.lateral_distribution = lateral_distribution * 2
                    else:
                        action.lateral_distribution = lateral_distribution

            if self.is_valid(row, 'apply_resistance'):
                action.apply_resistance = row['apply_resistance'].lower() == "true"
            if self.is_valid(row, 'speed', False):
                if row['speed'] == 'no_speed':  # TODO this needs to be fixed in spreadsheet
                    row['speed'] = 'none'
                action.speed = MovementSpeed[row['speed']]
            if self.is_valid(row, 'resistance', False):
                action.resistance = MovementResistance[row['resistance']]
            # if 'speed' in row.index and 'resistance' in row.index and self.is_valid(row, 'speed', False) and self.is_valid(row, 'resistance', False):
            #     action.explosiveness = self.get_explosiveness_from_speed_resistance(row['speed'], row['resistance'])
            if action.speed is not None and action.resistance is not None:
                action.explosiveness = self.get_explosiveness_from_speed_resistance(action.speed, action.resistance)
            else:
                if self.is_valid(row, 'relative_explosiveness'):
                    if row['relative_explosiveness'] == 'no_speed':
                        row['relative_explosiveness'] = 'no_force'
                    action.explosiveness = Explosiveness[row['relative_explosiveness']]
            if self.is_valid(row, 'apply_instability'):
                action.apply_instability = row['apply_instability'].lower() == "true"

            # primary
            if self.is_valid(row, 'muscle_action'):
                action.primary_muscle_action = MuscleAction[row['muscle_action']]

            action.hip_joint_action = self.get_prioritized_joint_actions(row, 'hip_joint')
            action.knee_joint_action = self.get_prioritized_joint_actions(row, 'knee_joint')
            action.ankle_joint_action = self.get_prioritized_joint_actions(row, 'ankle_joint')
            action.pelvic_tilt_joint_action = self.get_prioritized_joint_actions(row, 'pelvic_tilt_joint')
            action.trunk_joint_action = self.get_prioritized_joint_actions(row, 'trunk_joint')
            action.shoulder_scapula_joint_action = self.get_prioritized_joint_actions(row, 'shoulder_scapula_joint')
            action.elbow_joint_action = self.get_prioritized_joint_actions(row, 'elbow_joint')
            action.wrist_joint_action = self.get_prioritized_joint_actions(row, 'wrist_joint')

            # TODO: ignore secondary for now. Maybe relevant later
            # secondary
            # if self.is_valid(row, 'muscle_action'):
            #     pass
            # if self.is_valid(row, 'hip_stability'):
            #     pass
            # if self.is_valid(row, 'ankle_stability'):
            #     pass
            # if self.is_valid(row, 'trunk_stability_fm'):
            #     pass
            # if self.is_valid(row, 'pelvis_stability_fm'):
            #     pass
            # if self.is_valid(row, 'shoulder_stability'):
            #     pass
            # if self.is_valid(row, 'elbow_stability'):
            #     pass
            # if self.is_valid(row, 'sij_stability'):
            #     pass
            return action
        else:
            return None

    def get_prioritized_joint_actions(self, row, joint):

        res = []
        if self.is_valid(row, f'{joint}_action'):
            if self.is_valid(row, f'{joint}_priority'):
                joint_priority = int(row[f'{joint}_priority'])
                joint_actions = row[f'{joint}_action']
                joint_actions = joint_actions.replace(", ", ",")
                joint_actions = joint_actions.replace(" ", "_")
                joint_actions = joint_actions.replace("w/", "with")
                joint_actions = joint_actions.lower().split(",")
                joint_actions = [joint_action.split("\n") for joint_action in joint_actions]
                all_joint_actions = []
                for j_actions in joint_actions:
                    all_joint_actions.extend(j_actions)
                cleaned_joint_action = []
                for joint_action in all_joint_actions:
                    if joint_action in mapping.keys():
                        cleaned_joint_action.append(mapping[joint_action])
                    else:
                        cleaned_joint_action.append(joint_action)
                for j_action in cleaned_joint_action:
                    try:
                        res.append(PrioritizedJointAction(joint_priority, FunctionalMovementType[j_action]))
                    except:
                        print(j_action)

                    # return [PrioritizedJointAction(joint_priority, FunctionalMovementType[j_action]) for j_action in cleaned_joint_action]
                # except:
                #     print(cleaned_joint_action)
        return res

    @staticmethod
    def is_valid(row, name, check_none=True):
        if row.get(name) is not None and row[name] != "":
            if check_none:
                if row[name] != "none":
                    return True
            else:
                return True
        return False

    def get_actions_json(self):
        actions_json = {}
        for action in self.actions:
            actions_json[action.id] = action.json_serialise(initial_read=True)
        return actions_json

    # @staticmethod
    # def get_speed(speed):
    #     speed_conversion_dict = {
    #         'no_speed': 'none',
    #         'speed': 'slow',
    #         'normal': 'mod',
    #         'max_speed': 'fast'
    #     }
    #     if speed in speed_conversion_dict:
    #         speed = speed_conversion_dict[speed]
    #     return MovementSpeed[speed]


    @staticmethod
    def write_actions_json(actions_json):
        # actions_json = sorted(actions_json.items())
        json_string = json.dumps(actions_json, indent=4)
        file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/actions_library.json")
        # file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/actions_library_running.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()

    @staticmethod
    def get_explosiveness_from_speed_resistance(speed, resistance):
        # if speed == 'no_speed':  # TODO this needs to be fixed in spreadsheet
        #     speed = 'none'
        explosiveness_dict = {
            'none': {'none': 'no_force', 'slow': 'no_force', 'mod': 'no_force', 'fast': 'high_force', 'explosive': 'high_force'},
            'low': {'none': 'low_force', 'slow': 'low_force', 'mod': 'low_force', 'fast': 'high_force', 'explosive': 'high_force'},
            'mod': {'none': 'mod_force', 'slow': 'mod_force', 'mod': 'mod_force', 'fast': 'high_force', 'explosive': 'high_force'},
            'high': {'none': 'high_force', 'slow': 'high_force', 'mod': 'high_force', 'fast': 'max_force', 'explosive': 'max_force'},
            'max': {'none': 'high_force', 'slow': 'high_force', 'mod': 'high_force', 'fast': 'max_force', 'explosive': 'max_force'},
        }
        # if speed is not None and speed != "" and resistance is not None and resistance != "":
        resistance_dict = explosiveness_dict.get(resistance.name)
        if resistance_dict is not None:
            explosiveness = resistance_dict.get(speed.name)
            if explosiveness is None:
                print('here')
            return Explosiveness[explosiveness]
        return Explosiveness.no_force

mapping = {
    "shoulder_flexion": "shoulder_flexion_and_scapular_upward_rotation",
    "shoulder_extension": "shoulder_extension_and_scapular_downward_rotation",
    "shoulder_horizontal_adduction_(horizontal_flexion)": "shoulder_horizontal_adduction",
    "shoulder_adduction": "shoulder_horizontal_adduction",
    'shoulder_horizontal_abduction_(horizontal_extension)': "shoulder_horizontal_abduction",
    "shoulder_abduction": "shoulder_horizontal_abduction",
    "shoulder_internal_rotation": "internal_rotation",
    "shoulder_external_rotation": "external_rotation",
    "ankle_inversion": "ankle_dorsiflexion_and_inversion",
    "ankle_eversion": "ankle_plantar_flexion_and_eversion",
    "ankle_dorsi_flexion_and_eversion": "ankle_dorsiflexion_and_eversion",
    "ankle_dorsi_flexion_and_inversion": "ankle_dorsiflexion_and_inversion",
    "posterior_pelvic_tilt": "pelvic_posterior_tilt",
    "anterior_pelvic_tilt": "pelvic_anterior_tilt"

}

if __name__ == '__main__':
    action_parser = ActionLibraryParser()
    # action_parser.load_data("_demo")
    # action_parser.load_data(["_demo", "_running"])
    # TODO: cardio sheet is incomplete, use the old _running sheet for now
    action_parser.load_data(["_running", "_strength_integrated_resistance", "_power_action_plyometrics"])

