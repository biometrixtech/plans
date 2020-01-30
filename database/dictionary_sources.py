def get_equipment_dictionary():

    equipment_dict = {}
    equipment_dict["equipment: barbells"] = ["barbells", "barbell", "w/barbell", "bb"]
    equipment_dict["equipment: dumbbells"] = ["dumbbells", "dumbbell", "dumbell", "kettlebell/dumbbell", "db", "dummbell"]
    equipment_dict["equipment: kettlebells"] = ["kettlebells", "kettlebell", "kettlebell/dumbbell", "kb"]
    equipment_dict["equipment: sandbags"] = ["sandbags", "sandbag", "sandbag-"]
    equipment_dict["equipment: atlas stones"] = ["atlas stones", "atlas stone", "stone"]
    equipment_dict["equipment: yoke"] = ["yoke"]
    equipment_dict["equipment: dip belt"] = ["dip belt"]
    equipment_dict["equipment: medicine-slam balls"] = ["medicine ball", "slam ball", "med-ball", "medball"]
    equipment_dict["equipment: sled"] = ["sled"]
    equipment_dict["equipment: farmer's carry handles"] = ["farmer carry", "farmer' carry", "farmers carry", "farmer's carry"]
    equipment_dict["equipment: rower"] = ["rower", "row-pronated", "row-supinated", "row"]
    equipment_dict["equipment: airbike"] = ["airdyne"]
    equipment_dict["equipment: bike"] = ["bike"]
    equipment_dict["equipment: skiErg"] = ["skier", "ski"]
    equipment_dict["equipment: ruck"] = ["ruck"]
    equipment_dict["equipment: swimming"] = ["swim", "swimming"]
    equipment_dict["equipment: running"] = ["run", "running"]
    equipment_dict["equipment: elliptical trainer"] = ["elliptical"]
    equipment_dict["equipment: cables"] = ["cable", "cables"]
    equipment_dict["equipment: swiss balls"] = ["swis", "swiss"]
    equipment_dict["equipment: treadmill"] = ["treadmill"]

    return equipment_dict


def get_body_position_dictionary():

    dict = {}

    dict["body position: supine"] = ["supine", "supinated", "\(supine\)", "row-supinated"]
    dict["body position: prone"] = ["prone", "\(prone\)", "row-pronated", "pronated"]
    dict["body position: side lying"] = ["sidelying", "side lying", "side-lying"]
    dict["body position: kneeling"] = ["kneeling", "\(kneeling", "half-kneeling"]
    dict["body position: double leg standing"] = ["double leg"]
    dict["body position: split leg standing"] = ["split leg"]
    dict["body position: single leg standing"] = ["single leg"]
    dict["body position: alternating leg stance"] = ["alternating leg stance"]

    return dict


def get_direction_of_movement_dictionary():

    dict = {}

    dict["movement direction - plane: sagittal"] = ["sagittal", "flexion", "extension", "w/extension", "flexion/extension"]
    dict["movement direction - plane: frontal"] = ["adductor", "adduction", "abduction", "lateral"]
    dict["movement direction - plane: transverse"] = ["transverse", "internal/external", "internal", "external", "rotations-", "extension-rotation", "rotation", "rotational", "w/rotation"]
    dict["movement direction - axis: vertical"] = ["vertical"]
    dict["movement direction - axis: lateral"] = ["lateral", "medial"]
    dict["movement direction - axis: horizontal"] = ["horizontal", "anterior", "posterior"]
    dict["movement direction - axis: rotational"] = ["rotations-", "extension-rotation", "rotation", "rotational", "w/rotation"]
    
    return dict


def get_basic_execise_dictionary():

    dict = {
                    # "basic_exercise: push-ups": ["push up", "push ups", "push-up", "push-ups"],
                    # "basic_exercise: pull-ups": ["pull up", "pull ups", "pull-up", "pull-ups", "chip up", "chin-up", "chin ups", "chin-ups"],
                    # "basic_exercise: box jumps": ["box jump", "box jumps", "box-jump", "box-jumps"],
                    # "basic_exercise: depth jumps": ["depth jump", "depth jumps", "depth-jump", "depth-jumps"],
                    # "basic_exercise: dips": ["dip", "dips"],
                    # "basic_exercise: row": ["row", "rows"],
                    "basic_exercise: broad jumps": ["broad jump", "broad jumps", "broad-jump", "broad-jumps"],
                    "basic_exercise: vertical jumps": ["vertical jump", "vertical jumps", "vertical-jump", "vertical-jumps"],
                    "basic_exercise: bench press": ["bench press", "bench presses"],
                    "basic_exercise: step-up": ["step-ups", "step-up", "step up", "step ups"],
                    "basic_exercise: carry": ["carry", "carries", "carrys"],
                    "basic_exercise: press": ["press", "db press", "dumbell press", "dumbbell press", "dummbell press"],
                    "basic_exercise: fly": ["fly", "flys"],
                    "basic_exercise: shrug": ["shrug", "shrugs"],
                    # "basic_exercise: pull": ["pull", "pulls"],
                    "basic_exercise: curls": ["curl", "curls"],
                    "basic_exercise: thrusters": ["thruster", "thrusters"]
                    # "basic_exercise: extension": ["extension", "extensions"],
                    # "basic_exercise: pushdowns": ["pushdown", "pushdowns"],
                    # "basic_exercise: raises": ["raise", "raises"],
    }
    return dict


def get_olympic_lift_dictionary():
    dict = {
                    "olympic_lift: hang clean": ["hang clean", "hang cleans", "hang-clean", "hang-cleans", "hanging cleans", "hanging clean", "hanging-clean", "hanging-cleans"],
                    "olympic_lift: power clean": ["power clean", "power cleans", "power-clean", "power-cleans"],
                    "olympic_lift: push press": ["push press", "push-press", "push presses", "push-presses"],
                    "olympic_lift: clean and press": ["clean and press", "clean press", "clean and presses", "clean and presses"],
                    "olympic_lift: deadlift": ["deadlift", "deadlifts", "deadlit"],
                    "olympic_lift: snatch": ["snatch", "snatches"],
                    "olympic_lift: romanian deadlift": ["romanian deadlift", "romanian deadlifts", "rdl", "rdls"],
                    "olympic_lift: clean and jerk": ["clean and jerk", "clean jerk", "clean and jerks", "clean and jerk"],
                    "olympic_lift: cleans": ["clean", "cleans"],
                    "olympic_lift: jerks": ["jerk", "jerks"]
    }
    return dict


def get_basic_functional_movement_dictionary():
    dict = {
        # running
        # "basic_functional_movement: step": ["step", "steps", "walk", "walks", "walkings", "walkings"],
        # "basic_functional_movement: run": ["run", "runs", "running", "runnings"],
        # "basic_functional_movement: sprint": ["sprint", "sprints", "sprinting"],
        # "basic_functional_movement: cut": ["cut", "cuts"],
        # "basic_functional_movement: jump": ["jump", "jumps", "hop", "hops", "jumping"],
        # "basic_functional_movement: skip": ["skip", "skips"],
        # "basic_functional_movement: high knee": ["high knee", "high knees"],
        # "basic_functional_movement: backstroke": ["backstroke", "backstrokes"],

        # lower body
        # "basic_functional_movement: squat": ["squat", "squats"],
        # "basic_functional_movement: lunge": ["lunge", "lunges"],
        # "basic_functional_movement: hinge": ["hinge", "hinges"],
        # "basic_functional_movement: side step": ["side step", "side-step", "side steps", "side-steps"],
        # "basic_functional_movement: hip": ["hip", "hip"],
        # "basic_functional_movement: adductor": ["adductor", "adductor"],
        # "basic_functional_movement: leg lift": ["leg lift", "leg lift"],
        # "basic_functional_movement: leg extensions": ["leg extension", "leg-extension", "leg extensions", "leg-extensions"],
        # # core
        # "basic_functional_movement: stabilizer": ["plank", "planks", "sit-up", "sit up", "sit-ups", "sit-ups", "crunch", "crunches"],
        # "basic_functional_movement: dead bugs": ["dead bug", "deag bugs"],
        # "basic_functional_movement: v-ups": ["v up", "v-up", "v ups", "v-ups"],
        # "basic_functional_movement: with rotation": [],
        #
        # # upper body
        # "basic_functional_movement: throw": ["throw", "throws"],
        # "basic_functional_movement: row": ["row", "rows"],
        # "basic_functional_movement: Flexion": [], # (moving the arm upward in the Sagittal plane)
        # "basic_functional_movement: Extension": [], # (moving the arm down in the Sagittal plane)
        # "basic_functional_movement: Adduction": [], # (moving the upper arm down to the side toward the body)
        # "basic_functional_movement: Abduction": [], # (Lateral movement away from the midline of the body in the frontal plane, moving the upper arm up to the side away from the body)
        # "basic_functional_movement: Transverse Adduction": [], #
        # "basic_functional_movement: Transverse Flexion": [], #
        # "basic_functional_movement: Transverse Abduction": [], #
        # "basic_functional_movement: Transverse Extension": [], #
        # "basic_functional_movement: Medial rotation": [], #
        # "basic_functional_movement: Lateral rotation": [], #
        # "basic_functional_movement: With Trunk Rotation": [], #

        "dynamic_activity: step": ["step", "steps", "walk", "walks", "walkings", "walkings"],
        "dynamic_activity: run": ["run", "runs", "running", "runnings"],
        "dynamic_activity: sprint": ["sprint", "sprints", "sprinting"],
        "dynamic_activity: cut": ["cut", "cuts"],
        "dynamic_activity: jump": ["jump", "jumps", "hop", "hops", "jumping"],
        "dynamic_activity: skip": ["skip", "skips"],
        "dynamic_activity: high knee": ["high knee", "high knees"],
        "dynamic_activity: backstroke": ["backstroke", "backstrokes"],

        # lower body
        "lower_body: squat": ["squat", "squats"],
        "lower_body: lunge": ["lunge", "lunges"],
        "lower_body: hinge": ["hinge", "hinges"],
        "lower_body: side step": ["side step", "side-step", "side steps", "side-steps"],
        "lower_body: hip": ["hip", "hip"],
        "lower_body: adductor": ["adductor", "adductor"],
        "lower_body: leg lift": ["leg lift", "leg lift"],
        "lower_body: leg extensions": ["leg extension", "leg-extension", "leg extensions", "leg-extensions"],
        "lower_body: leg curls": ["leg curl", "leg curls", "hamstring curl", "hamstring curls"],
        "lower_body: leg raises": ["leg raise", "leg raises", "calf raise", "calf raises"],
        "lower_body: box jumps": ["box jump", "box jumps", "box-jump", "box-jumps"],
        "lower_body: depth jumps": ["depth jump", "depth jumps", "depth-jump", "depth-jumps"],
        # core
        "core: stabilizer": ["plank", "planks", "sit-up", "sit up", "sit-ups", "sit-ups", "crunch", "crunches"],
        "core: dead bugs": ["dead bug", "dead bugs"],
        "core: v-ups": ["v up", "v-up", "v ups", "v-ups"],
        "core: with rotation": [],

        # upper body
        "upper_body: throw": ["throw", "throws"],
        "upper_body: dips": ["dip", "dips"],
        "upper_body: row": ["row", "rows"],
        "upper_body: push-ups": ["push up", "push ups", "push-up", "push-ups"],
        "upper_body: pull-ups": ["pull up", "pull ups", "pull-up", "pull-ups", "chip up", "chin-up", "chin ups", "chin-ups"],
        "upper_body: raises": ["db raise",  "db raises", "dumbbell raise", "dumbbell raises","dumbell raise","dumbell raises"],
        "upper_body: tricep": ["tricep", "triceps"],
        "upper_body: biceps": ["bicep", "biceps"],
        "upper_body: chest": ["chest"],
        "upper_body: shoulder": ["shoulder", "shoulders"]
    }
    return dict


def get_all_dict():
    all_dicts = {}
    all_dicts.update(get_basic_execise_dictionary())
    all_dicts.update(get_olympic_lift_dictionary())
    # all_dicts.update(get_equipment_dictionary())
    # all_dicts.update(get_body_position_dictionary())
    # all_dicts.update(get_direction_of_movement_dictionary())
    all_dicts.update(get_basic_functional_movement_dictionary())
    return all_dicts
