from enum import Enum


class FunctionalMovementType(Enum):
    ankle_dorsiflexion = 0
    ankle_plantar_flexion = 1
    inversion_of_the_foot = 2
    eversion_of_the_foot = 3
    ankle_dorsiflexion_and_inversion = 4
    ankle_plantar_flexion_and_eversion = 5
    knee_flexion = 6
    knee_extension = 7
    tibial_external_rotation = 8
    tibial_internal_rotation = 9
    hip_adduction = 10
    hip_abduction = 11
    hip_internal_rotation = 12
    hip_external_rotation = 13
    hip_extension = 14
    hip_flexion = 15
    hip_horizontal_abduction = 16
    hip_horizontal_adduction = 17
    pelvic_anterior_tilt = 18
    pelvic_posterior_tilt = 19
    trunk_flexion = 20
    trunk_extension = 21
    trunk_lateral_flexion = 22
    trunk_rotation = 23
    trunk_flexion_with_rotation = 24
    trunk_extension_with_rotation = 25
    elbow_flexion = 26
    elbow_extension = 27
    shoulder_horizontal_adduction = 28
    shoulder_horizontal_abduction = 29
    shoulder_flexion_and_scapular_upward_rotation = 30
    shoulder_extension_and_scapular_downward_rotation = 31
    shoulder_abduction_and_scapular_upward_rotation = 32
    shoulder_adduction_and_scapular_downward_rotation = 33
    internal_rotation = 34
    external_rotation = 35
    scapular_elevation = 36
    scapular_depression = 37
    ankle_dorsiflexion_and_eversion = 38
    ankle_plantar_flexion_and_inversion = 39
    wrist_flexion = 40
    wrist_extension = 41
