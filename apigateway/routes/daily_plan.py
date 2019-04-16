from flask import request, Blueprint
import datetime

from utils import format_date, format_datetime, parse_datetime
from datastores.datastore_collection import DatastoreCollection
from logic.athlete_status_processing import AthleteStatusProcessing

from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder

datastore_collection = DatastoreCollection()
daily_plan_datastore = datastore_collection.daily_plan_datastore

app = Blueprint('daily_plan', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@require.body({'start_date': str})
@xray_recorder.capture('routes.daily_plan.get')
def handle_daily_plan_get(principal_id=None):
    validate_input()
    user_id = principal_id
    event_date = request.json.get('event_date', format_datetime(datetime.datetime.utcnow()))
    event_date = parse_datetime(event_date)

    # start_date = request.json['start_date']
    # if 'end_date' in request.json:
    #     end_date = request.json['end_date']
    # else:
    #     start_date = format_date(event_date)
    #     end_date = start_date
    # items = daily_plan_datastore.get(user_id, start_date, end_date)
    # daily_plans = []
    # need_soreness_sessions = False
    # for plan in items:
    #     survey_complete = plan.daily_readiness_survey_completed()
    #     if plan.event_date == format_date(event_date) and not survey_complete:
    #         need_soreness_sessions = True
    #     landing_screen, nav_bar_indicator = plan.define_landing_screen()
    #     plan = plan.json_serialise()
    #     plan['daily_readiness_survey_completed'] = survey_complete
    #     plan['landing_screen'] = landing_screen
    #     plan['nav_bar_indicator'] = nav_bar_indicator
    #     del plan['daily_readiness_survey'], plan['user_id']
    #     daily_plans.append(plan)
    # if need_soreness_sessions:
    #     previous_soreness_processor = AthleteStatusProcessing(user_id, event_date, datastore_collection=datastore_collection)
    #     (
    #         sore_body_parts,
    #         hist_sore_status,
    #         clear_candidates,
    #         dormant_tipping_candidates,
    #         current_sport_name,
    #         current_position,
    #         functional_strength_eligible,
    #         completed_functional_strength_sessions
    #     ) = previous_soreness_processor.get_previous_soreness()
    #     readiness = {
    #                   'body_parts': sore_body_parts,
    #                   'dormant_tipping_candidates': dormant_tipping_candidates,
    #                   'hist_sore_status': hist_sore_status,
    #                   'clear_candidates': clear_candidates,
    #                   'current_position': current_position,
    #                   'current_sport_name': current_sport_name,
    #                   'functional_strength_eligible': functional_strength_eligible,
    #                   'completed_functional_strength_sessions': completed_functional_strength_sessions
    #                  }

    #     typical_sessions = previous_soreness_processor.get_typical_sessions()
    # else:
    #     readiness = {}
    #     typical_sessions = []

    # return {'daily_plans': daily_plans,
    #         'readiness': readiness,
    #         'typical_sessions': typical_sessions}, 200
    return {'daily_plans': [temp_plan(format_date(event_date))],
            'readiness': {},
            'typical_sessions': {}}


def validate_input():
    try:
        format_date(request.json['start_date'])
        format_date(request.json.get('end_date', None))
        format_datetime(request.json.get('event_date', None))
    except Exception:
        raise InvalidSchemaException('Incorrectly formatted date')

def temp_plan(date):
    return {
            "completed_functional_strength_sessions": 0,
            "completed_post_recovery_sessions": [],
            "daily_readiness_survey_completed": True,
            "date": date,
            "day_of_week": 1,
            "functional_strength_completed": False,
            "functional_strength_eligible": False,
            "functional_strength_session": None,
            "landing_screen": 0,
            "last_updated": "2019-04-16T16:40:57Z",
            "nav_bar_indicator": 0,
            "post_recovery": {
                "1": {
                        "activate_exercises": [],
                        "activate_iterations": 0,
                        "completed": False,
                        "display_exercises": False,
                        "event_date": None,
                        "inhibit_exercises": [],
                        "integrate_exercises": [],
                        "lengthen_exercises": [],
                        "minutes_duration": 0,
                        "start_date": None},
                "2": {
                        "activate_exercises": [],
                        "activate_iterations": 0,
                        "completed": False,
                        "display_exercises": False,
                        "event_date": None,
                        "inhibit_exercises": [],
                        "integrate_exercises": [],
                        "lengthen_exercises": [],
                        "minutes_duration": 0,
                        "start_date": None},
                "3": {
                        "activate_exercises": [],
                        "activate_iterations": 0,
                        "completed": False,
                        "display_exercises": False,
                        "event_date": None,
                        "inhibit_exercises": [],
                        "integrate_exercises": [],
                        "lengthen_exercises": [],
                        "minutes_duration": 0,
                        "start_date": None}
            },
            "pre_recovery": {
                "1": {
                    "activate_exercises": [
                        {
                            "bilateral": False,
                            "description": "Begin on your hands and knees with your back flat. Simultaneously raise the right arm and left leg until the extended arm and leg are horizontal. Hold for 1-2 seconds, then bring your arm and leg back down. Alternate sides as you complete the set number of reps.",
                            "display_name": "Bird-dog",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Increase strength",
                            "library_id": "50",
                            "name": "Quadruped Arm/Opposite Leg Raise",
                            "position_order": 6,
                            "reps_assigned": 10,
                            "seconds_duration": 90,
                            "seconds_per_rep": 3,
                            "seconds_per_set": None,
                            "sets_assigned": 3,
                            "unit_of_measure": "count",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "Lay on your side on a bed or table with your lower legs hanging off. Pull the knee of your top leg toward you and keep it at the same height as you rotate your hips so your foot moves above and below your knee. ",
                            "display_name": "Windshield Wipers",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Increase strength",
                            "library_id": "229",
                            "name": "Windshield Wipers",
                            "position_order": 7,
                            "reps_assigned": 10,
                            "seconds_duration": 80,
                            "seconds_per_rep": 2,
                            "seconds_per_set": None,
                            "sets_assigned": 2,
                            "unit_of_measure": "count",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "On your side with one leg lifted off the ground and slightly behind your body, move your leg in small clockwise circles. Maintain a flexed foot so your toes are pointing towards you.",
                            "display_name": "Leg Circles",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Increase strength",
                            "library_id": "232",
                            "name": "Small Clockwise Circles",
                            "position_order": 8,
                            "reps_assigned": 10,
                            "seconds_duration": 80,
                            "seconds_per_rep": 2,
                            "seconds_per_set": None,
                            "sets_assigned": 2,
                            "unit_of_measure": "count",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "Begin on your side with your elbow positioned under your shoulder and your legs stacked, knees bent. Place your other hand on your hip and lift off the ground, keeping your body in a straight line.",
                            "display_name": "Side Plank (Knees Bent)",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Increase strength",
                            "library_id": "89",
                            "name": "Side Plank Knees Bent",
                            "position_order": 9,
                            "reps_assigned": 30,
                            "seconds_duration": 120,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 2,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [0, 1]
                        },
                        {
                            "bilateral": False,
                            "description": "Lie on your back with your legs straight and your arms overhead. Bend your hips and knees. Contract your abdomen so your low back is flush with the ground. Move one leg and the opposite arm to the ground, straightening the knee and hip to bring the leg just above the ground. Engage your core and return the working limbs to the starting position.",
                            "display_name": "Dead Bugs",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Increase strength",
                            "library_id": "84",
                            "name": "Supine Arm/Leg Raise - Dying Bugs",
                            "position_order": 10,
                            "reps_assigned": 10,
                            "seconds_duration": 40,
                            "seconds_per_rep": 2,
                            "seconds_per_set": None,
                            "sets_assigned": 2,
                            "unit_of_measure": "count",
                            "youtube_id": None,
                            "goals": [1]
                        }
                    ],
                    "completed": False,
                    "display_exercises": True,
                    "event_date": None,
                    "inhibit_exercises": [
                        {
                            "bilateral": True,
                            "description": "Begin on your stomach with a foam roller beneath one thigh. Keeping that foot off of the ground, shift your weight onto that leg as you roll the length of the muscle from the knee to the hip, holding points of tension for 30 seconds. Switch sides and repeat. Don’t have a foam roller? You can use a tennis ball or water bottle.",
                            "display_name": "Foam Roll - Quads",
                            "equipment_required": [
                                "Foam Roller"
                            ],
                            "goal_text": "Increase flexibility",
                            "library_id": "48",
                            "name": "Foam Roller Quadriceps",
                            "position_order": 0,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "Place foam roller just before the glute & roll the length of your hamstring. If you find a tender spot, hold for 30 seconds. Don’t have a foam roller? You can use a tennis ball or water bottle. ",
                            "display_name": "Foam Roll - Hamstrings",
                            "equipment_required": [
                                "Foam Roller"
                            ],
                            "goal_text": "Increase flexibility",
                            "library_id": "3",
                            "name": "Foam Roller - Hamstrings",
                            "position_order": 1,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "On your side, slowly foam roll from the outer hip joint down toward the knee. If you find a tender spot, hold for 30 seconds. Don’t have a foam roller? You can use a tennis ball or water bottle.",
                            "display_name": "Foam Roll - Outer Thigh",
                            "equipment_required": [
                                "Foam Roller"
                            ],
                            "goal_text": "Increase flexibility",
                            "library_id": "4",
                            "name": "Foam Roller - IT-Band",
                            "position_order": 2,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [2]
                        }],
                    "integrate_exercises": [],
                    "lengthen_exercises": [
                        {
                            "bilateral": True,
                            "description": "In a plank position, raise your hips up and back and lengthen through your shoulders. Try to press your heels toward the ground to feel a stretch through the back of your lower leg.",
                            "display_name": "Kneeling Hamstring Stretch",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Prepare for movement",
                            "library_id": "216",
                            "name": "Kneeling Hamstring Stretch",
                            "position_order": 3,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "Stand with one leg in front of the other. Raise the arm that is on the same side as your back leg, engaging your core as you lean backward until a stretch is felt in your hip. Rotate the shoulder of your raised arm back to deepen the stretch. ",
                            "display_name": "Standing Hip Stretch",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Prepare for movement",
                            "library_id": "6",
                            "name": "Hip Flexor Static Stretch (Standing)",
                            "position_order": 4,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [2]
                        },
                        {
                            "bilateral": True,
                            "description": "Begin in a standing position with your toes pointing forward. Turn one foot to the outisde. With the opposite foot step forward into a lunge position, keeping your hips facing the front. Place your hands on your hips for balance.",
                            "display_name": "Standing Outer Hip Stretch",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Prepare for movement",
                            "library_id": "28",
                            "name": "Standing TFL Static Stretch",
                            "position_order": 5,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [2]
                        }],
                    "minutes_duration": 15,
                    "start_date": None
                },
                "2": {
                    "activate_exercises": [
                            {
                                "bilateral": False,
                                "description": "Begin on your hands and knees with your back flat. Simultaneously raise the right arm and left leg until the extended arm and leg are horizontal. Hold for 1-2 seconds, then bring your arm and leg back down. Alternate sides as you complete the set number of reps.",
                                "display_name": "Bird-dog",
                                "equipment_required": [
                                    "None"
                                ],
                                "goal_text": "Increase strength",
                                "library_id": "50",
                                "name": "Quadruped Arm/Opposite Leg Raise",
                                "position_order": 6,
                                "reps_assigned": 10,
                                "seconds_duration": 90,
                                "seconds_per_rep": 3,
                                "seconds_per_set": None,
                                "sets_assigned": 3,
                                "unit_of_measure": "count",
                                "youtube_id": None,
                                "goals": [0]
                            },
                            {
                                "bilateral": True,
                                "description": "Lay on your side on a bed or table with your lower legs hanging off. Pull the knee of your top leg toward you and keep it at the same height as you rotate your hips so your foot moves above and below your knee. ",
                                "display_name": "Windshield Wipers",
                                "equipment_required": [
                                    "None"
                                ],
                                "goal_text": "Increase strength",
                                "library_id": "229",
                                "name": "Windshield Wipers",
                                "position_order": 7,
                                "reps_assigned": 10,
                                "seconds_duration": 80,
                                "seconds_per_rep": 2,
                                "seconds_per_set": None,
                                "sets_assigned": 2,
                                "unit_of_measure": "count",
                                "youtube_id": None,
                                "goals": [0]
                            },
                            {
                                "bilateral": True,
                                "description": "On your side with one leg lifted off the ground and slightly behind your body, move your leg in small clockwise circles. Maintain a flexed foot so your toes are pointing towards you.",
                                "display_name": "Leg Circles",
                                "equipment_required": [
                                    "None"
                                ],
                                "goal_text": "Increase strength",
                                "library_id": "232",
                                "name": "Small Clockwise Circles",
                                "position_order": 8,
                                "reps_assigned": 10,
                                "seconds_duration": 80,
                                "seconds_per_rep": 2,
                                "seconds_per_set": None,
                                "sets_assigned": 2,
                                "unit_of_measure": "count",
                                "youtube_id": None,
                                "goals": [0]
                            },
                            {
                                "bilateral": True,
                                "description": "Begin on your side with your elbow positioned under your shoulder and your legs stacked, knees bent. Place your other hand on your hip and lift off the ground, keeping your body in a straight line.",
                                "display_name": "Side Plank (Knees Bent)",
                                "equipment_required": [
                                    "None"
                                ],
                                "goal_text": "Increase strength",
                                "library_id": "89",
                                "name": "Side Plank Knees Bent",
                                "position_order": 9,
                                "reps_assigned": 30,
                                "seconds_duration": 120,
                                "seconds_per_rep": None,
                                "seconds_per_set": 30,
                                "sets_assigned": 2,
                                "unit_of_measure": "seconds",
                                "youtube_id": None,
                                "goals": [0, 1]
                            },
                            {
                                "bilateral": False,
                                "description": "Lie on your back with your legs straight and your arms overhead. Bend your hips and knees. Contract your abdomen so your low back is flush with the ground. Move one leg and the opposite arm to the ground, straightening the knee and hip to bring the leg just above the ground. Engage your core and return the working limbs to the starting position.",
                                "display_name": "Dead Bugs",
                                "equipment_required": [
                                    "None"
                                ],
                                "goal_text": "Increase strength",
                                "library_id": "84",
                                "name": "Supine Arm/Leg Raise - Dying Bugs",
                                "position_order": 10,
                                "reps_assigned": 10,
                                "seconds_duration": 40,
                                "seconds_per_rep": 2,
                                "seconds_per_set": None,
                                "sets_assigned": 2,
                                "unit_of_measure": "count",
                                "youtube_id": None,
                                "goals": [1]
                            }
                        ],
                        "completed": False,
                        "display_exercises": True,
                        "event_date": None,
                        "inhibit_exercises": [
                            {
                                "bilateral": True,
                                "description": "Begin on your stomach with a foam roller beneath one thigh. Keeping that foot off of the ground, shift your weight onto that leg as you roll the length of the muscle from the knee to the hip, holding points of tension for 30 seconds. Switch sides and repeat. Don’t have a foam roller? You can use a tennis ball or water bottle.",
                                "display_name": "Foam Roll - Quads",
                                "equipment_required": [
                                    "Foam Roller"
                                ],
                                "goal_text": "Increase flexibility",
                                "library_id": "48",
                                "name": "Foam Roller Quadriceps",
                                "position_order": 0,
                                "reps_assigned": 30,
                                "seconds_duration": 60,
                                "seconds_per_rep": None,
                                "seconds_per_set": 30,
                                "sets_assigned": 1,
                                "unit_of_measure": "seconds",
                                "youtube_id": None,
                                "goals": [0]
                            },
                            {
                                "bilateral": True,
                                "description": "Place foam roller just before the glute & roll the length of your hamstring. If you find a tender spot, hold for 30 seconds. Don’t have a foam roller? You can use a tennis ball or water bottle. ",
                                "display_name": "Foam Roll - Hamstrings",
                                "equipment_required": [
                                    "Foam Roller"
                                ],
                                "goal_text": "Increase flexibility",
                                "library_id": "3",
                                "name": "Foam Roller - Hamstrings",
                                "position_order": 1,
                                "reps_assigned": 30,
                                "seconds_duration": 60,
                                "seconds_per_rep": None,
                                "seconds_per_set": 30,
                                "sets_assigned": 1,
                                "unit_of_measure": "seconds",
                                "youtube_id": None,
                                "goals": [0]
                            },
                            {
                                "bilateral": True,
                                "description": "On your side, slowly foam roll from the outer hip joint down toward the knee. If you find a tender spot, hold for 30 seconds. Don’t have a foam roller? You can use a tennis ball or water bottle.",
                                "display_name": "Foam Roll - Outer Thigh",
                                "equipment_required": [
                                    "Foam Roller"
                                ],
                                "goal_text": "Increase flexibility",
                                "library_id": "4",
                                "name": "Foam Roller - IT-Band",
                                "position_order": 2,
                                "reps_assigned": 30,
                                "seconds_duration": 60,
                                "seconds_per_rep": None,
                                "seconds_per_set": 30,
                                "sets_assigned": 1,
                                "unit_of_measure": "seconds",
                                "youtube_id": None,
                                "goals": [2]
                            }
                        ],
                        "integrate_exercises": [],
                        "lengthen_exercises": [
                            {
                                "bilateral": True,
                                "description": "In a plank position, raise your hips up and back and lengthen through your shoulders. Try to press your heels toward the ground to feel a stretch through the back of your lower leg.",
                                "display_name": "Kneeling Hamstring Stretch",
                                "equipment_required": [
                                    "None"
                                ],
                                "goal_text": "Prepare for movement",
                                "library_id": "216",
                                "name": "Kneeling Hamstring Stretch",
                                "position_order": 3,
                                "reps_assigned": 30,
                                "seconds_duration": 60,
                                "seconds_per_rep": None,
                                "seconds_per_set": 30,
                                "sets_assigned": 1,
                                "unit_of_measure": "seconds",
                                "youtube_id": None,
                                "goals": [0]
                            },
                            {
                                "bilateral": True,
                                "description": "Stand with one leg in front of the other. Raise the arm that is on the same side as your back leg, engaging your core as you lean backward until a stretch is felt in your hip. Rotate the shoulder of your raised arm back to deepen the stretch. ",
                                "display_name": "Standing Hip Stretch",
                                "equipment_required": [
                                    "None"
                                ],
                                "goal_text": "Prepare for movement",
                                "library_id": "6",
                                "name": "Hip Flexor Static Stretch (Standing)",
                                "position_order": 4,
                                "reps_assigned": 30,
                                "seconds_duration": 60,
                                "seconds_per_rep": None,
                                "seconds_per_set": 30,
                                "sets_assigned": 1,
                                "unit_of_measure": "seconds",
                                "youtube_id": None,
                                "goals": [2]
                            },
                            {
                                "bilateral": True,
                                "description": "Begin in a standing position with your toes pointing forward. Turn one foot to the outisde. With the opposite foot step forward into a lunge position, keeping your hips facing the front. Place your hands on your hips for balance.",
                                "display_name": "Standing Outer Hip Stretch",
                                "equipment_required": [
                                    "None"
                                ],
                                "goal_text": "Prepare for movement",
                                "library_id": "28",
                                "name": "Standing TFL Static Stretch",
                                "position_order": 5,
                                "reps_assigned": 30,
                                "seconds_duration": 60,
                                "seconds_per_rep": None,
                                "seconds_per_set": 30,
                                "sets_assigned": 1,
                                "unit_of_measure": "seconds",
                                "youtube_id": None,
                                "goals": [2]
                            }
                        ],
                        "minutes_duration": 15,
                        "start_date": None
                    },
                "3": {
                    "activate_exercises": [
                        {
                            "bilateral": False,
                            "description": "Begin on your hands and knees with your back flat. Simultaneously raise the right arm and left leg until the extended arm and leg are horizontal. Hold for 1-2 seconds, then bring your arm and leg back down. Alternate sides as you complete the set number of reps.",
                            "display_name": "Bird-dog",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Increase strength",
                            "library_id": "50",
                            "name": "Quadruped Arm/Opposite Leg Raise",
                            "position_order": 6,
                            "reps_assigned": 10,
                            "seconds_duration": 90,
                            "seconds_per_rep": 3,
                            "seconds_per_set": None,
                            "sets_assigned": 3,
                            "unit_of_measure": "count",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "Lay on your side on a bed or table with your lower legs hanging off. Pull the knee of your top leg toward you and keep it at the same height as you rotate your hips so your foot moves above and below your knee. ",
                            "display_name": "Windshield Wipers",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Increase strength",
                            "library_id": "229",
                            "name": "Windshield Wipers",
                            "position_order": 7,
                            "reps_assigned": 10,
                            "seconds_duration": 80,
                            "seconds_per_rep": 2,
                            "seconds_per_set": None,
                            "sets_assigned": 2,
                            "unit_of_measure": "count",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "On your side with one leg lifted off the ground and slightly behind your body, move your leg in small clockwise circles. Maintain a flexed foot so your toes are pointing towards you.",
                            "display_name": "Leg Circles",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Increase strength",
                            "library_id": "232",
                            "name": "Small Clockwise Circles",
                            "position_order": 8,
                            "reps_assigned": 10,
                            "seconds_duration": 80,
                            "seconds_per_rep": 2,
                            "seconds_per_set": None,
                            "sets_assigned": 2,
                            "unit_of_measure": "count",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "Begin on your side with your elbow positioned under your shoulder and your legs stacked, knees bent. Place your other hand on your hip and lift off the ground, keeping your body in a straight line.",
                            "display_name": "Side Plank (Knees Bent)",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Increase strength",
                            "library_id": "89",
                            "name": "Side Plank Knees Bent",
                            "position_order": 9,
                            "reps_assigned": 30,
                            "seconds_duration": 120,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 2,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [0, 1]
                        },
                        {
                            "bilateral": False,
                            "description": "Lie on your back with your legs straight and your arms overhead. Bend your hips and knees. Contract your abdomen so your low back is flush with the ground. Move one leg and the opposite arm to the ground, straightening the knee and hip to bring the leg just above the ground. Engage your core and return the working limbs to the starting position.",
                            "display_name": "Dead Bugs",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Increase strength",
                            "library_id": "84",
                            "name": "Supine Arm/Leg Raise - Dying Bugs",
                            "position_order": 10,
                            "reps_assigned": 10,
                            "seconds_duration": 40,
                            "seconds_per_rep": 2,
                            "seconds_per_set": None,
                            "sets_assigned": 2,
                            "unit_of_measure": "count",
                            "youtube_id": None,
                            "goals": [1]
                        }
                    ],
                    "completed": False,
                    "display_exercises": True,
                    "event_date": None,
                    "inhibit_exercises": [
                        {
                            "bilateral": True,
                            "description": "Begin on your stomach with a foam roller beneath one thigh. Keeping that foot off of the ground, shift your weight onto that leg as you roll the length of the muscle from the knee to the hip, holding points of tension for 30 seconds. Switch sides and repeat. Don’t have a foam roller? You can use a tennis ball or water bottle.",
                            "display_name": "Foam Roll - Quads",
                            "equipment_required": [
                                "Foam Roller"
                            ],
                            "goal_text": "Increase flexibility",
                            "library_id": "48",
                            "name": "Foam Roller Quadriceps",
                            "position_order": 0,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "Place foam roller just before the glute & roll the length of your hamstring. If you find a tender spot, hold for 30 seconds. Don’t have a foam roller? You can use a tennis ball or water bottle. ",
                            "display_name": "Foam Roll - Hamstrings",
                            "equipment_required": [
                                "Foam Roller"
                            ],
                            "goal_text": "Increase flexibility",
                            "library_id": "3",
                            "name": "Foam Roller - Hamstrings",
                            "position_order": 1,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "On your side, slowly foam roll from the outer hip joint down toward the knee. If you find a tender spot, hold for 30 seconds. Don’t have a foam roller? You can use a tennis ball or water bottle.",
                            "display_name": "Foam Roll - Outer Thigh",
                            "equipment_required": [
                                "Foam Roller"
                            ],
                            "goal_text": "Increase flexibility",
                            "library_id": "4",
                            "name": "Foam Roller - IT-Band",
                            "position_order": 2,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [2]
                        }
                    ],
                    "integrate_exercises": [],
                    "lengthen_exercises": [
                        {
                            "bilateral": True,
                            "description": "In a plank position, raise your hips up and back and lengthen through your shoulders. Try to press your heels toward the ground to feel a stretch through the back of your lower leg.",
                            "display_name": "Kneeling Hamstring Stretch",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Prepare for movement",
                            "library_id": "216",
                            "name": "Kneeling Hamstring Stretch",
                            "position_order": 3,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [0]
                        },
                        {
                            "bilateral": True,
                            "description": "Stand with one leg in front of the other. Raise the arm that is on the same side as your back leg, engaging your core as you lean backward until a stretch is felt in your hip. Rotate the shoulder of your raised arm back to deepen the stretch. ",
                            "display_name": "Standing Hip Stretch",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Prepare for movement",
                            "library_id": "6",
                            "name": "Hip Flexor Static Stretch (Standing)",
                            "position_order": 4,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [2]
                        },
                        {
                            "bilateral": True,
                            "description": "Begin in a standing position with your toes pointing forward. Turn one foot to the outisde. With the opposite foot step forward into a lunge position, keeping your hips facing the front. Place your hands on your hips for balance.",
                            "display_name": "Standing Outer Hip Stretch",
                            "equipment_required": [
                                "None"
                            ],
                            "goal_text": "Prepare for movement",
                            "library_id": "28",
                            "name": "Standing TFL Static Stretch",
                            "position_order": 5,
                            "reps_assigned": 30,
                            "seconds_duration": 60,
                            "seconds_per_rep": None,
                            "seconds_per_set": 30,
                            "sets_assigned": 1,
                            "unit_of_measure": "seconds",
                            "youtube_id": None,
                            "goals": [2]
                        }
                    ],
                    "minutes_duration": 15,
                    "start_date": None
                    }
                },
            
            "post_recovery_completed": False,
            "pre_recovery_completed": False,
            "session_from_readiness": False,
            "sessions_planned": True,
            "sessions_planned_readiness": True,
            "training_sessions": []
    }
