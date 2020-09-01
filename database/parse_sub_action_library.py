from models.movement_actions import CompoundAction, ExerciseAction, ExerciseSubAction, UpperBodyStance, LowerBodyStance, Explosiveness, MuscleAction, PrioritizedJointAction, MovementSpeed, MovementResistance, PrioritizedMovementSystem
from models.movement_tags import TrainingType, Equipment, WeightDistribution, BodyPosition
from models.functional_movement_type import FunctionalMovementType
from models.soreness_base import BodyPartSystems
from copy import deepcopy
import os
import json
import pandas as pd


class SubActionLibraryParser(object):
    def __init__(self):
        #self.actions_pd = None
        self.actions = []
        self.sub_actions = {}
        self.sub_action_lookup = {}

    def load_sub_actions(self, sub_action_files):

        self.sub_actions = {}

        for sub_action_file in sub_action_files:
            actions_pd = pd.read_csv(f'Fathom Sub Action Library/sub actions: {sub_action_file}.csv', keep_default_na=False, skiprows=1)

            last_sub_action = ExerciseAction(None, None)

            for index, row in actions_pd.iterrows():
                if self.is_import_done(row):
                    break
                if self.is_not_header_row(row):
                    action_item = self.parse_sub_action_row(row, last_sub_action)
                    last_sub_action = action_item
                    if action_item is not None:
                        if action_item.id not in self.sub_actions:
                            self.sub_actions[action_item.id] = action_item
                            self.sub_action_lookup[action_item.id] = action_item.name
                        else:
                            self.sub_actions[action_item.id].movement_systems.extend(action_item.movement_systems)
                            self.sub_actions[action_item.id].hip_joint_action.extend(action_item.hip_joint_action)
                            self.sub_actions[action_item.id].knee_joint_action.extend(action_item.knee_joint_action)
                            self.sub_actions[action_item.id].ankle_joint_action.extend(action_item.ankle_joint_action)
                            self.sub_actions[action_item.id].pelvic_tilt_joint_action.extend(action_item.pelvic_tilt_joint_action)
                            self.sub_actions[action_item.id].trunk_joint_action.extend(action_item.trunk_joint_action)
                            self.sub_actions[action_item.id].shoulder_scapula_joint_action.extend(action_item.shoulder_scapula_joint_action)
                            self.sub_actions[action_item.id].elbow_joint_action.extend(action_item.elbow_joint_action)
                            self.sub_actions[action_item.id].wrist_joint_action.extend(action_item.wrist_joint_action)

    def load_compound_actions(self, compound_action_files):
        """

        :param compound_actoin_files: prioritized ordered list of file suffix.
                      If the same action occurs in second file as the first one, data from first file will be discarded
        :return:
        """
        actions_json = {}

        for compound_action_file in compound_action_files:

            actions_pd = pd.read_csv(f'Fathom Compound Action Library/Compound Actions: {compound_action_file}-Compound Action Library.csv', keep_default_na=False, skiprows=1)

            compound_action = CompoundAction(None, None)

            rows = []

            self.actions = []

            for index, row in actions_pd.iterrows():

                if self.is_valid(row, 'id'): # action id
                    if compound_action.id is None or (len(row['compound_action_id']) > 0 and compound_action.id != row['compound_action_id']):
                        if len(rows) > 0 and compound_action.id is not None and (len(row['compound_action_id']) > 0 and compound_action.id != row['compound_action_id']):
                            compound_action = self.parse_compound_action_row(rows, compound_action)
                            self.actions.append(compound_action)
                        rows = [row]
                        compound_action = CompoundAction(row['compound_action_id'],
                                                         row['compound_action_name'])

                        if self.is_valid(row, 'training_type'):
                            try:
                                compound_action.training_type = self.get_training_type(row['training_type'])
                            except:
                                return None

                        if self.is_valid(row, 'eligible_external_resistance'):
                            row['eligible_external_resistance'] = row[
                                'eligible_external_resistance'].replace(", ", ",")
                            resistances = row.get('eligible_external_resistance').lower().split(",")
                            try:
                                compound_action.eligible_external_resistance = [Equipment[ex_res] for ex_res in
                                                                                resistances]
                            except:
                                print(f"eligible_external_resistance: {row['eligible_external_resistance']}")

                        if self.is_valid(row, 'resistance', False):
                            compound_action.resistance = MovementResistance[row['resistance']]

                        if self.is_valid(row, 'speed', False):
                            if row['speed'] == 'no_speed':  # TODO this needs to be fixed in spreadsheet
                                row['speed'] = 'none'
                            compound_action.speed = self.get_speed(row['speed'])

                        # TODO - how does this related to sub-action body position?
                        if self.is_valid(row, 'body_position'):
                            compound_action.body_position = BodyPosition[row['body_position']]

                    elif compound_action.id is not None:
                        rows.append(row)
                else:
                    if len(rows) > 0 and compound_action.id is not None:
                        compound_action = self.parse_compound_action_row(rows, compound_action)
                        self.actions.append(compound_action)
                        rows = []
            if len(rows) > 0 and compound_action.id is not None:
                compound_action = self.parse_compound_action_row(rows, compound_action)
                self.actions.append(compound_action)

            actions_json_file = self.get_actions_json()
            actions_json.update(actions_json_file)

        self.write_actions_json(actions_json)

    def parse_compound_action_row(self, rows, compound_action):

        action = ExerciseAction(None, None)

        for row in rows:
            if action.id is None or action.id != row['id']:
                if action.id is not None:
                    compound_action.actions.append(action)
                action = ExerciseAction(row['id'], "")

            if self.is_valid(row, 'sub_action_id'):
                sub_action_id = row['sub_action_id']

                if sub_action_id in self.sub_actions:
                    sub_action = self.sub_actions[sub_action_id]

                    new_subaction = ExerciseSubAction(sub_action_id, sub_action.name)
                    new_subaction.training_type = compound_action.training_type
                    new_subaction.eligible_external_resistance = compound_action.eligible_external_resistance
                    new_subaction.speed = compound_action.speed
                    new_subaction.resistance = compound_action.resistance
                    new_subaction.body_position = compound_action.body_position

                    # items inherited from compound action (if populated)
                    if self.is_valid(row, 'contribute_to_power_production'):
                        new_subaction.contribute_to_power_production = row['contribute_to_power_production'].lower() == "true"
                    else:
                        new_subaction.contribute_to_power_production = sub_action.contribute_to_power_production

                    if self.is_valid(row, 'apply_instability'):
                        new_subaction.apply_instability = row['apply_instability'].lower() == "true"
                    else:
                        new_subaction.apply_instability = sub_action.apply_instability

                    if self.is_valid(row, 'apply_resistance'):
                        new_subaction.apply_resistance = row['apply_resistance'].lower() == "true"
                    else:
                        new_subaction.apply_resistance = sub_action.apply_resistance

                    if self.is_valid(row, 'stance_lower_body'):
                        new_subaction.lower_body_stance = LowerBodyStance[row['stance_lower_body']]
                    else:
                        new_subaction.lower_body_stance = sub_action.lower_body_stance

                    if self.is_valid(row, 'stance_upper_body'):
                        new_subaction.upper_body_stance = UpperBodyStance[row['stance_upper_body']]
                    else:
                        new_subaction.upper_body_stance = sub_action.upper_body_stance

                    if self.is_valid(row, 'lateral_distribution_pattern'):
                        new_subaction.lateral_distribution_pattern = WeightDistribution[
                            row['lateral_distribution_pattern']]
                    else:
                        new_subaction.lateral_distribution_pattern = sub_action.lateral_distribution_pattern

                        # New
                    # if self.is_valid(row, 'arm'):
                    #     new_subaction.arm = row['arm']
                    # else:
                    #     new_subaction.arm = sub_action.arm
                    # if self.is_valid(row, 'torso'):
                    #     new_subaction.torso = row['torso']
                    # else:
                    #     new_subaction.torso = sub_action.torso
                    # if self.is_valid(row, 'leg'):
                    #     new_subaction.leg = row['leg']
                    # else:
                    #     new_subaction.leg = sub_action.leg
                    # if self.is_valid(row, 'multiplier'):
                    #     new_subaction.multiplier = row['multiplier']
                    # else:
                    #     new_subaction.multiplier = sub_action.multiplier

                    if self.is_valid(row, 'percent_bodyweight'):
                        new_subaction.percent_bodyweight = int(float(row.get('percent_bodyweight', 0)))
                    else:
                        new_subaction.percent_bodyweight = sub_action.percent_bodyweight

                    if self.is_valid(row, 'lateral_distribution'):
                        lateral_distribution = row['lateral_distribution'].split(',')
                        try:
                            lateral_distribution = [int(float(val.strip())) for val in lateral_distribution]
                        except ValueError:
                            print(lateral_distribution)
                        else:
                            if len(lateral_distribution) == 0:
                                new_subaction.lateral_distribution = [50, 50]
                            elif len(lateral_distribution) == 1:
                                new_subaction.lateral_distribution = lateral_distribution * 2
                            else:
                                new_subaction.lateral_distribution = lateral_distribution
                    else:
                        new_subaction.lateral_distribution = sub_action.lateral_distribution

                    # items unique to sub actions
                    new_subaction.muscle_action = sub_action.muscle_action

                    # New
                    new_subaction.movement_systems = sub_action.movement_systems

                    new_subaction.hip_joint_action = sub_action.hip_joint_action
                    new_subaction.knee_joint_action = sub_action.knee_joint_action
                    new_subaction.ankle_joint_action = sub_action.ankle_joint_action
                    new_subaction.pelvic_tilt_joint_action = sub_action.pelvic_tilt_joint_action
                    new_subaction.trunk_joint_action = sub_action.trunk_joint_action
                    new_subaction.shoulder_scapula_joint_action = sub_action.shoulder_scapula_joint_action
                    new_subaction.elbow_joint_action = sub_action.elbow_joint_action
                    new_subaction.wrist_joint_action = sub_action.wrist_joint_action

                    # TODO - we doing this again???
                    new_subaction.body_position = sub_action.body_position

                    action.sub_actions.append(new_subaction)
                else:
                    print("ERROR: SUBACTION NOT FOUND")

        if action.id is not None:
            compound_action.actions.append(action)

        return compound_action

    def parse_sub_action_row(self, row, last_sub_action):

        if row['sub_action_id'] is not None and row['sub_action_id'] != '':
            subaction_name = row['sub_action_name']
            if row['sub_action_id'] in self.sub_action_lookup:
                subaction_name = self.sub_action_lookup[row['sub_action_id']]
            if last_sub_action.id is None or last_sub_action.id != row['sub_action_id']:
                action = ExerciseSubAction(row['sub_action_id'], subaction_name)
            else:
                action = deepcopy(last_sub_action)

            if self.is_valid(row, 'muscle_action'):
                action.muscle_action = MuscleAction[row['muscle_action']]

            # New
            if self.is_valid(row, 'movement_system'):
                action.movement_systems = self.get_prioritized_movement_system(row)

            action.hip_joint_action = self.get_prioritized_joint_actions(row, 'hip_joint')
            action.knee_joint_action = self.get_prioritized_joint_actions(row, 'knee_joint')
            action.ankle_joint_action = self.get_prioritized_joint_actions(row, 'ankle_joint')
            action.pelvic_tilt_joint_action = self.get_prioritized_joint_actions(row, 'pelvic_tilt_joint')
            action.trunk_joint_action = self.get_prioritized_joint_actions(row, 'trunk_joint')
            action.shoulder_scapula_joint_action = self.get_prioritized_joint_actions(row, 'shoulder_scapula_joint')
            action.elbow_joint_action = self.get_prioritized_joint_actions(row, 'elbow_joint')
            action.wrist_joint_action = self.get_prioritized_joint_actions(row, 'wrist_joint')

            if self.is_valid(row, 'body_position'):
                action.body_position = BodyPosition[row['body_position']]

            # New
            if self.is_valid(row, 'eligible_external_resistance'):
                row['eligible_external_resistance'].replace(", ", ",")
                external_weight_implement = row['eligible_external_resistance'].lower().split(",")
                try:
                    action.eligible_external_resistance = [Equipment[equipment] for equipment in external_weight_implement]
                except:
                    print('here', external_weight_implement)

            if self.is_valid(row, 'contribute_to_power_production'):
                action.contribute_to_power_production = row['contribute_to_power_production'].lower() == "true"

            if self.is_valid(row, 'apply_instability'):
                action.apply_instability = row['apply_instability'].lower() == "true"
            if self.is_valid(row, 'apply_resistance'):
                action.apply_resistance = row['apply_resistance'].lower() == "true"

            if self.is_valid(row, 'stance_lower_body'):
                action.lower_body_stance = LowerBodyStance[row['stance_lower_body']]
            if self.is_valid(row, 'stance_upper_body'):
                action.upper_body_stance = UpperBodyStance[row['stance_upper_body']]

            if self.is_valid(row, 'lateral_distribution_pattern'):
                action.lateral_distribution_pattern = WeightDistribution[row['lateral_distribution_pattern']]

            # New
            # if self.is_valid(row, 'arm'):
            #     action.arm = row['arm']
            # if self.is_valid(row, 'torso'):
            #     action.torso = row['torso']
            # if self.is_valid(row, 'leg'):
            #     action.leg = row['leg']
            # if self.is_valid(row, 'multiplier'):
            #     action.multiplier = row['multiplier']

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

            return action
        else:
            return None

    def is_import_done(self, row):
        if 'to be deleted' in row['sub_action_id']:
            return True
        else:
            return False

    def is_not_header_row(self, row):
        sub_id = row['sub_action_id']
        if len(sub_id) == 0:
            return False
        else:
            return sub_id[0].isnumeric()

    def get_speed(self, speed):
        # speed_conversion_dict = {
        #     'no_speed': 'none',
        #     'speed': 'slow',
        #     'normal': 'mod',
        #     'max_speed': 'fast'
        # }
        # if speed in speed_conversion_dict:
        #     speed = speed_conversion_dict[speed]
        if 'speed' in speed:
            speed = speed.split('_')[0]
        elif speed == "high":
            speed = "fast"
        return MovementSpeed[speed]

    def get_training_type(self, training_type):
        if training_type in ['strength_core','strength_action_bw']:
            training_type_value = TrainingType.strength_endurance
        else:
            training_type_value = TrainingType[training_type]

        return training_type_value

    def get_prioritized_movement_system(self, row):

        if self.is_valid(row, 'movement_system'):
            if self.is_valid(row, 'movement_system_priority'):
                priority = int(row['movement_system_priority'])
                movement_system_name = row['movement_system']
                prioritized_movement_system = PrioritizedMovementSystem(priority, movement_system_name)
                return [prioritized_movement_system]
        return []

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
        file_name = os.path.join(os.path.realpath('..'), f"apigateway/fml/actions_library.json")
        # file_name = os.path.join(os.path.realpath('..'), f"apigateway/models/actions_library_running.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()

    # @staticmethod
    # def get_explosiveness_from_speed_resistance(speed, resistance):
    #     # if speed == 'no_speed':  # TODO this needs to be fixed in spreadsheet
    #     #     speed = 'none'
    #     explosiveness_dict = {
    #         'none': {'none': 'no_force', 'slow': 'no_force', 'mod': 'no_force', 'fast': 'high_force', 'explosive': 'high_force'},
    #         'low': {'none': 'low_force', 'slow': 'low_force', 'mod': 'low_force', 'fast': 'high_force', 'explosive': 'high_force'},
    #         'mod': {'none': 'mod_force', 'slow': 'mod_force', 'mod': 'mod_force', 'fast': 'high_force', 'explosive': 'high_force'},
    #         'high': {'none': 'high_force', 'slow': 'high_force', 'mod': 'high_force', 'fast': 'max_force', 'explosive': 'max_force'},
    #         'max': {'none': 'high_force', 'slow': 'high_force', 'mod': 'high_force', 'fast': 'max_force', 'explosive': 'max_force'},
    #     }
    #     # if speed is not None and speed != "" and resistance is not None and resistance != "":
    #     resistance_dict = explosiveness_dict.get(resistance.name)
    #     if resistance_dict is not None:
    #         explosiveness = resistance_dict.get(speed.name)
    #         if explosiveness is None:
    #             print('here')
    #         return Explosiveness[explosiveness]
    #     return Explosiveness.no_force

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
    action_parser = SubActionLibraryParser()
    # action_parser.load_data("_demo")
    # action_parser.load_data(["_demo", "_running"])
    # TODO: cardio sheet is incomplete, use the old _running sheet for now
    action_parser.load_sub_actions(["Cardio-Table 1", "PosturalStability-Table 1", "Strength-Table 1"])
    action_parser.load_compound_actions(["Cardio", "Strength", "Power", ])
    j=0

