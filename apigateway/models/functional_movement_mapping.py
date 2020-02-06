from models.movement_actions import ExerciseAction


class ActionMappingMovementFactory(object):

    def get_functional_movement_mappings(self, action_id):

        mapping = []

        action = ExerciseAction("1", "Test")

        mapping.append(action)

        return mapping

