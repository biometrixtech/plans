from models.workout_program import AdaptationType, Movement, TrainingType


class WorkoutProcessor(object):

    def get_movements_for_workout_exercise(self, workout_exercise):

        movements = []

        movement = Movement()

        movements.append(movement)

        return movements


class MovementProcessor(object):

    def get_adaptation_type(self, movement):

        if movement.training_type == TrainingType.flexibility:
            return AdaptationType.not_tracked
        elif movement.training_type == TrainingType.cardiorespiratory:
            return AdaptationType.strength_endurance_cardiorespiratory
        elif movement.training_type == TrainingType.core:
            return AdaptationType.strength_endurance_strength
        elif movement.training_type == TrainingType.balance:
            return AdaptationType.strength_endurance_strength
        elif movement.training_type == TrainingType.plyometrics:
            return AdaptationType.power_explosive_action
        elif movement.training_type == TrainingType.plyometrics_drills:
            return AdaptationType.power_drill
        elif movement.training_type == TrainingType.speed_agility_quickness:
            return AdaptationType.power_drill
        elif movement.training_type == TrainingType.integrated_resistance:
            if movement.intensity >= 75:
                return AdaptationType.maximal_strength_hypertrophic
            else:
                return AdaptationType.strength_endurance_strength
        elif movement.training_type == TrainingType.olympic_lifting:
            if not movement.explosive:
                return AdaptationType.maximal_strength_hypertrophic
            else:
                return AdaptationType.power_explosive_action
        else:
            return

    def get_exercise_intensity_for_olympic_lifting(self, olympic_lifting_type):

        pass
