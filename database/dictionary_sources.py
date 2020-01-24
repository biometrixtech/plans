def get_equipment_dictionary():

    equipment_dict = {}
    equipment_dict["equipment: barbells"] = ["barbells", "barbell", "w/barbell"]
    equipment_dict["equipment: dumbbells"] = ["dumbbells", "dumbbell", "dumbell", "kettlebell/dumbbell"]
    equipment_dict["equipment: kettlebells"] = ["kettlebells", "kettlebell", "kettlebell/dumbbell"]
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

    dict["body position: supine"] = ["supine", "supinated", "(supine)", "row-supinated"]
    dict["body position: prone"] = ["prone", "(prone)", "row-pronated", "pronated"]
    dict["body position: side lying"] = ["sidelying", "side lying"]
    dict["body position: kneeling"] = ["kneeling", "(kneeling", "half-kneeling"]
    dict["body position: double leg standing"] = ["double leg"]
    dict["body position: split leg standing"] = ["split leg"]
    dict["body position: single leg standing"] = ["single leg"]
    dict["body position: alternating leg stance"] = ["alternating leg stance"]

    return dict


def get_direction_of_movement_dictionary():

    dict = {}

    dict["movement direction - plane: sagittal"] = ["sagittal", "flexion", "extension", "w/extension", "flexion/extension"]
    dict["movement direction - plane: frontal"] = ["front", "adductor", "adduction", "abduction", "lateral"]
    dict["movement direction - plane: transverse"] = ["transverse", "internal/external", "internal", "external", "rotations-", "extension-rotation", "rotation", "rotational", "w/rotation"]
    dict["movement direction - axis: vertical"] = ["vertical"]
    dict["movement direction - axis: lateral"] = ["lateral", "medial"]
    dict["movement direction - axis: horizontal"] = ["horizontal", "anterior", "posterior"]
    dict["movement direction - axis: rotational"] = ["rotations-", "extension-rotation", "rotation", "rotational", "w/rotation"]
    
    return dict


