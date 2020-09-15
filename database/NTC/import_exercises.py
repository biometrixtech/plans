import os
import json
import pandas as pd
from models.movement_actions import Movement, MovementSpeed, MovementResistance, MovementDisplacement, MuscleAction, ActionsForPower
from models.movement_tags import TrainingType, MovementSurfaceStability, Equipment, BodyPosition, WeightDistribution


class ClientExercise(object):
    def __init__(self, name):
        self.name = name
        self.base_movement_id = None
        self.base_movement_name = None
        self.client_exercise_name = None

        self.training_type = None
        self.bilateral_distribution_of_resistance = None
        self.resistance = None
        self.speed = None
        self.displacement = None
        self.surface_stability = None
        self.external_weight_implement = []
        self.rest_between_reps = 0
        self.rep_tempo = []
        self.involvement = None
        self.plane = None
        self.body_position = None
        self.upper_body_symmetry = None
        self.actions_for_power = []
        # self.percent_bodyweight = []
        # self.percent_bodyheight = []
        # self.time = []
        # self.muscle_action = []
        # self.description = []

    def json_serialise(self):
        ret = {
            'name': self.name,
            'base_movement_id': self.base_movement_id,
            'base_movement_name': self.base_movement_name,
            'client_exercise_name': self.client_exercise_name,
            'training_type': self.training_type.value if self.training_type is not None else None,
            'bilateral_distribution_of_resistance': self.bilateral_distribution_of_resistance.value if self.bilateral_distribution_of_resistance is not None else None,
            'resistance': self.resistance.value if self.resistance is not None else None,
            'speed': self.speed.value if self.speed is not None else None,
            'displacement': self.displacement.value if self.displacement is not None else None,
            'surface_stability': self.surface_stability.value if self.surface_stability is not None else None,
            'external_weight_implement': [equip.value for equip in self.external_weight_implement],
            'rest_between_reps': self.rest_between_reps,
            'rep_tempo': self.rep_tempo,
            'involvement': self.involvement,
            'plane': self.plane,
            'body_position': self.body_position.value if self.body_position is not None else None,
            'upper_body_symmetry': self.upper_body_symmetry,
            'actions_for_power': [ap.json_serialise() for ap in self.actions_for_power]

            # 'percent_bodyweight': self.percent_bodyweight,
            # 'percent_bodyheight': self.percent_bodyheight,
            # 'time': self.time,
            # 'muscle_action': self.muscle_action,
            # 'description': self.description
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        ex = cls(input_dict['name'])
        ex.base_movement_id = input_dict.get('base_movement_id')
        ex.base_movement_name = input_dict.get('base_movement_name')
        ex.client_exercise_name = input_dict.get('client_exercise_name')
        ex.training_type = TrainingType(input_dict['training_type'])
        ex.bilateral_distribution_of_resistance = WeightDistribution(input_dict['bilateral_distribution_of_resistance']) if input_dict.get('bilateral_distribution_of_resistance') is not None else None
        ex.resistance = MovementResistance(input_dict['resistance']) if input_dict.get('resistance') is not None else None
        ex.speed = MovementSpeed(input_dict['speed']) if input_dict.get('speed') is not None else None
        ex.displacement = MovementDisplacement(input_dict['displacement']) if  input_dict.get('displacement') is not None else None
        ex.surface_stability = MovementSurfaceStability(input_dict['surface_stability']) if input_dict.get('surface_stability') is not None else None
        ex.external_weight_implement = [Equipment(equip) for equip in input_dict.get('external_weight_implement', [])]
        ex.rest_between_reps = input_dict.get('rest_between_reps')
        ex.rep_tempo = input_dict.get('rep_tempo')
        ex.involvement = input_dict.get('involvement')
        ex.plane = input_dict.get('plane')
        ex.body_position = BodyPosition(input_dict['body_position']) if input_dict.get('body_position') is not None else None
        ex.upper_body_symmetry = input_dict.get('upper_body_symmetry')
        ex.actions_for_power = [ActionsForPower.json_deserialise(ap) for ap in input_dict.get('actions_for_power', [])]
        return ex


class ExerciseParser(object):
    def __init__(self):
        self.exercise_pd = None
        self.exercises = []
        self.training_type_lookup = {
            'strength_core': 'strength_endurance',
            'strength_action_bw': 'strength_endurance'
        }
        self.equipment_name_loookup = {
            'kettlebell': 'kettlebells'
        }
        self.resistance_lookup = {
            'no_resistance': 'none'
        }
        self.speed_lookup = {
            'no_speed': 'none',
            'low': 'slow'
        }
        self.displacement_lookup = {
            'Full ROM': 'full_rom'
        }


    def load_data(self, files):
        """

        :param files: list of files to import
        :return:
        """
        all_exercises = []

        all_rep_tempos = set()
        for file in files:
            self.exercise_pd = pd.read_csv(f'exercise_to_base_movement/{file}', keep_default_na=False)

            self.exercise_pd.rename(columns={'speed (as rep tempo or as max action pace)': 'speed'}, inplace=True)
            self.exercises = []

            for index, row in self.exercise_pd.iterrows():
                exercise = self.parse_row(row)
                if exercise is not None:
                    self.exercises.append(exercise)
                    # if exercise.rep_tempo != '':
                    #     all_rep_tempos.add(exercise.rep_tempo)

            exercise_json = self.get_exercise_json()
            all_exercises.extend(exercise_json)
        #
        # for rep_tempo in all_rep_tempos:
        #     print(rep_tempo)
        all_movements = list({ex['base_movement_name'] for ex in all_exercises})
        all_movements.sort()


        self.write_json(all_exercises)

    def parse_row(self, row):
        if (row['nike_exercise_name'] is not None and row['nike_exercise_name'] != ''):
            name = row['nike_exercise_name'].strip().lower()
            ex = ClientExercise(name)
            ex.base_movement_name = row['base_movement_name'].strip().lower()
            training_type = self.training_type_lookup.get(row['training_type']) or row['training_type']
            ex.training_type = TrainingType[training_type]
            if self.is_valid(row['bilateral_distribution_of_resistance']):
                if len(row['bilateral_distribution_of_resistance'].split(',')) > 1:
                    row['bilateral_distribution_of_resistance'] = row['bilateral_distribution_of_resistance'].split(',')[0]
                ex.bilateral_distribution_of_resistance = WeightDistribution[row['bilateral_distribution_of_resistance']]
            if self.is_valid(row['resistance']):
                ex.resistance = MovementResistance[self.resistance_lookup.get(row['resistance']) or row['resistance']]
            if self.is_valid(row['speed']):
                ex.speed = MovementSpeed[self.speed_lookup.get(row['speed']) or row['speed']]
            if 'displacement' in row:
                if self.is_valid(row['displacement']):
                    displacement = ('_').join(row['displacement'].strip().lower().split(' '))
                    ex.displacement = MovementDisplacement[displacement]
            if self.is_valid(row['rest_between_reps']):
                ex.rest_between_reps = float(row['rest_between_reps'])

            if self.is_valid(row['rep_tempo']):
                rep_tempos = []
                all_rep_tempos = row['rep_tempo'].split(';')
                for rep_tempo in all_rep_tempos:
                    # rep_tempo = row['rep_tempo']
                    rep_tempo.replace(' ', '')
                    rep_tempo = rep_tempo.split('/')
                    rep_tempo = [float(dur) for dur in rep_tempo]
                    rep_tempos.extend(rep_tempo)
                ex.rep_tempo = rep_tempos
            if self.is_valid(row['surface_stability']):
                ex.surface_stability = MovementSurfaceStability[row['surface_stability']]
            ex.involvement = row['involvement']
            ex.plane = row['plane']
            if self.is_valid(row['body_position']):
                ex.body_position = BodyPosition[row['body_position']]
            ex.upper_body_symmetry = row['upper_body_symmetry']
            if self.is_valid(row['external_weight_implement']):
                ex.external_weight_implement = [Equipment[self.equipment_name_loookup.get(row['external_weight_implement'].lower()) or row['external_weight_implement'].lower()]]
            try:
                ex.actions_for_power = self.get_actions_for_power(row)
            except KeyError:
                print(ex.name)
            except Exception as e:
                print(e)
                print(ex.name)
                pass
            return ex

        return None

    def get_actions_for_power(self, row):
        actions_for_power = []
        if 'percent_bodyweight' in row:
            all_bodyweights = []
            all_bodyheights = []
            all_times = []
            all_muscle_actions = []
            if self.is_valid(row['percent_bodyweight']):
                sim_actions = row['percent_bodyweight'].split(';')
                for action in sim_actions:
                    bodyweights = action.replace(" ", "").split('/')
                    bodyweights = (float(bw) / 100 for bw in bodyweights)
                    all_bodyweights.append(list(bodyweights))

            if self.is_valid(row['percent_bodyheight']):
                sim_actions = row['percent_bodyheight'].split(';')
                for action in sim_actions:
                    bodyheights = action.replace(" ", "").replace("unknown", "-1000").split('/')
                    bodyheights = (float(bh) / 100 for bh in bodyheights)
                    all_bodyheights.append(list(bodyheights))

            if self.is_valid(row['muscle_action']):
                # sim_actions = row['muscle_action'].split(';')
                # if len(sim_actions) > 1:

                # all_muscle_actions = []
                # for action in sim_actions:
                muscle_actions = row['muscle_action'].replace(" ", "").split('/')
                muscle_actions = [MuscleAction[ma] for ma in muscle_actions if ma != ""]
                all_muscle_actions.extend(muscle_actions)
                # if len(all_times) != len(all_bodyweights):
                #     all_times *= 2

            if self.is_valid(row['Time']):
                # sim_actions = row['Time'].split(';')
                # all_times = []
                # for action in sim_actions:
                times = row['Time'].replace(" ", "").split('/')
                times = [float(time) for time in times]
                all_times.extend(times)
                # if len(all_times) != len(all_bodyweights):
                #     all_times *= 2
            for i in range(len(all_times)):
                ap = ActionsForPower()
                ap.muscle_action = all_muscle_actions[i]
                ap.time = all_times[i]
                for bodyweights in all_bodyweights:
                    ap.percent_bodyweight.append(bodyweights[i])
                for bodyheights in all_bodyheights:
                    ap.percent_bodyheight.append(bodyheights[i])
                # ap.percent_bodyweight = all_bodyweights[i]
                # ap.percent_bodyheight = all_bodyheights[i]
                actions_for_power.append(ap)
        return actions_for_power



    def get_exercise_json(self):
        return [ex.json_serialise() for ex in self.exercises]

    def write_json(self, all_exercises):
        json_string = json.dumps(all_exercises, indent=4)
        file_name = os.path.join(f"libraries/nike_exercises.json")
        print(f"writing: {file_name}")
        f1 = open(file_name, 'w')
        f1.write(json_string)
        f1.close()

    @staticmethod
    def is_valid(value):
        if value is not None and value != "":
            return True
        return False


if __name__ == '__main__':
    files = os.listdir('_NTC Exercise Library mapped to Fathom Base Movement/')
    # files = [file for file in files if 'bw' not in file]
    ExerciseParser().load_data(files)
    # all_data = []
    # for file in files:
    #     data = pd.read_csv(f"exercise_to_base_movement/{file}")
    #     all_data.append(data)

print('')