# FathomAI - Plans API (v 4.4.0)
## Technical Summary


### Overview

This technical summary provides prospective third party partners ('providers') of  __Fathom's Plans API__ with a brief summary of the type of information returned from the service along with a summary of the minimum technical and data requirements.  This document is not a substitute for the full API specification.

### Daily Plan

The plans service generates a  __Daily Plan__ for an athlete based on one or both of the following data elements:

* __Daily Readiness__ - information about the athlete's training plan and pain/soreness for a given day
* __Post-Workout__ - information about an athlete's workout session along with their Rating of Perceived Exertion (RPE) and pain/soreness following the workout

A __Daily Plan__ can be created with as little as one of the above data elements. As this information is gathered over time, Fathom's analytics also use historical patterns in pain/soreness and workouts to identify underlying imbalances unique to the athlete which influence the creation of their __Daily Plan__.

A __Daily Plan__ provides a personalized, research-driven prep, recovery, and corrective exercise plan for an athlete.  A plan may consist of one or more modalities, targeting one or more recovery goals Fathom analytics identifies for the athlete.

The __Daily Plan__ includes modalities such as  __foam rolling__, __static stretching__, __active stretching__, __dynamic stretching__, __targeted muscle activation__, and __integrated movement__ exercises personalized for the athlete for that day.  These exercises are provided in a sequence consistent with sports science research to expedite tissue recovery, reduce pain, and prevent injury.
 
Other modalities do not include exercises but are assigned to a plan based on athlete needs.  These modalities include __heat__, __ice__ and __cold water immersion__.

Recommended dosages are also provided for each exercise and modality.  These dosages are associated with three different active times which correspond with minimal, optimal, and comprehensive sequences of activities.  These sequences are designed to achieve each of the athlete's unique combination of goals.  Additionally, dosages are also provided by goal, allowing the athlete to further customize their recovery.


## Technical and Data Requirements

### Terminology

The terminology of [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt) (specifically __must__, __should__, __may__ and their negatives) applies.  The word __will__, when applied to the Plans API ("the API"), has the same meaning as __must__.

Each third-party partner will be recognised as a "provider" and will be assigned a unique 'Provider Code'.  This __will__ be a string matching the regular expression `^[a-z][a-z0-9\-]{3,31}$`.
  

### Protocol

The API supports communication over HTTPS only.  The client __must__ recognise the Amazon Trust Services LLC certificate root. 

### Encoding

The API supports communication using JSON encoding only.  The client __must__ submit the headers `Content-Type: application/json` and `Accept: application/json` (or a subtype `application/{subtype}+json`, if appropriate) for all requests.  Failure to do so __will__ result in a `415 Unsupported Media Type` response.  The API __will__ include the header `Content-Type: application/json` (or a subtype if appropriate) with its response.

### Endpoints

Each provider will also be assigned a unique set of test and production endpoints to access the plans service. 

### Authentication

Unless otherwise specified, the endpoints in the API are authenticated by a JWT bearer token.  The client __must__ submit the header `Authorization: <JWT>` with all requests. Failure to do so, or submitting an invalid or expired JWT, __will__ result in a `401 Unauthorized` response.  

It is expected that partners will normally generate and sign their own JWTs for their clients, providing appropriate authorization for each athlete in accordance with their business and compliance requirements.

#### Signing keys

Prior to integrating with the API, each partner  __must__ supply a set of one or more public keys with which they will sign clients' JWT credentials.  This __must__ take the form of an [RFC 7517](https://tools.ietf.org/html/rfc7517) JSON Web Key Set document, for example:

```json
{
    "keys": [
        {
            "kid": "fathom_001",
            "alg": "RS256",
            "kty": "RSA",
            "use": "sig",
            "e": "AQAB",
            "n": "snrCqqc2tC......Z29H9DBLIQ",
            "_env": ["dev", "test"]
        },
        {
            "kid": "fathom_002",
            "alg": "RS256",
            "kty": "RSA",
            "use": "sig",
            "e": "AQAB",
            "n": "yuHDihazrP......UuEPOofbVQ",
            "_env": "production"
        }
    ]
}
```

Each key within the key set  __must__ have a `kid` field matching the regular expression `^([a-z][a-z0-9\-]{3,31})_([a-z0-9\-]+)$`, where the first group of the expression is the partner's Provider Code.  

Each key within the key set  __must__ have a `use` field set to `sig` if the key is to be used for signing JWTs.  Partners __should not__ include keys with other values in the key set.

At the present time the only algorithm from the  [RFC 7518](https://tools.ietf.org/html/rfc7518#section-3) list supported is RSA-256, so the value of the `alg` field for each key in the key set __must__ be `RS256`.  We hope to support at least `ES256` in the near future.

Partners __may__ include the non-standardized fields `_nbf` and `_exp` in key definitions; if these fields are provided, they __must__ follow the semantics of the corresponding JWT claim fields in  [RFC7519](https://tools.ietf.org/html/rfc7519#section-4.1.3), and the API __will__ interpret them similarly (that is to say, a JWT with an `iat` value falling before the corresponding key's `nbf` value or after its `exp` value, will not be considered valid).  This allows partners to perform key rotation in an orderly fashion.

Partners __may__ include the non-standardized field `_env` in key definitions; if this field is provided the value  __must__ be a String matching the regular expression `^[a-z0-9]+$` or an array of such Strings, and the API  __will__ interpret this as a list of the environments where the key should be accepted.  This allows partners to use different signing keys for production and non-production environments.

#### JWT claims

The JWTs provided by clients  __must__ contain the following claims:

* `iss`, which __must__ be a String matching the regular expression `^([a-z][a-z0-9\-]{3,31})_([a-z0-9\-]+)$`, where the first group of the expression is the partner's Provider Code.  
* `aud`, which __must__ be a String matching the regular expression `^fathom(_[a-z0-9]+)?$` (or an array containing such a String).  If the group is provided (eg `fathom_production`), the API __will__ treat the second part as an environment specifier, and __will__ only accept as valid JWTs targeted at its own environment (for instance, the production API will only accept tokens with an `aud` value of `fathom` and/or `fathom_production`).
* `iat` __must__ be specified.
* `exp` __must__ be specified.  The total period of validity of the JWT (ie the time range between the lesser of `iat` and `nfb`, and `exp`) __must not__ be greater than 86400 seconds.
* `sub`, which __must__ be a Uuid identifying the athlete on whose behalf the client is acting.  In general the API will only allow requests which correspond to actions affecting this user.
* `scope`, which __must__ be a String containing a space-separated list of Scopes, where each Scope is a String matching the regular expression `^[a-z][a-z0-9\.:]*$`.  The following scopes are recognised by the API:
   * `fathom.plans:read`: provides access to read-only functionality for the athlete identified by the `sub` claim
   * `fathom.plans:write`: provides access to write functionality for the athlete identified by the `sub` claim.  This is a superset of `fathom.plans:read`.
   * `fathom.plans:service`: provides access to all functionality for all users.  JWTs with this scope are subject to additional validation conditions described below.

#### Service tokens

Partners __may__ interact with the API on a business-to-business basis instead of, or in addition to, building clients which allow users to interact with the API directly.  Partners' private servers __may__ authenticate such requests using a JWT carrying the `fathom.plans:service` scope.  Such tokens must meet the following additional validation conditions:

* The value of the `sub` field  __must__ be the String `00000000-0000-4000-8000-000000000000`.
* The total period of validity of the JWT  __must not__ be greater than 600 seconds.

### General responses

In addition to the API responses and the specific responses for each endpoint, the server  __may__ respond with one of the following HTTP responses:

* `400 Bad Request` with `Status` header equal to `InvalidSchema`, if the JSON body of the request does not match the requirements of the endpoint.
* `403 Forbidden` with `Status` header equal to `Forbidden`, if the user is not allowed to perform the requested action.
* `404 Unknown` with `Status` header equal to `UnknownEndpoint`, if an invalid endpoint was requested.

</br>

## Data Requirements

### Types

Required data elements are based on the following simple types :

* `string`, `number`, `integer`, `boolean`: as defined in the [JSON Schema](http://json-schema.org) standard.
* `Uuid`: a `string` matching the regular expression `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`, that is, the string representation of an  [RFC 4122](https://tools.ietf.org/html/rfc4122) UUID.
* `Datetime`: a `string` matching the regular expression `/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|+\d{2}:\d{2})/` and representing a date and time in full  [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) format.

### Daily Readiness

#### Required Data Elements

The following data elements are required when following the  __Daily Readiness__ pathway to __Daily Plan__ generation.

* `date_time` __should__ be a Datetime and reflect the local time that survey was taken
* `soreness` __should__ reflect a list of body parts(`sore_part`) with symptoms. Length __could__ be 0.

`sore_part` __should__ include the following:

* `body_part` __should__ be an integer reflecting BodyPart enum of the body part with symptom
* `side` __should__ be an integer, either 0 (both sides/non-bilateral), 1 (left) or 2 (right)
* `tight` __should__ be an integer (1-10) indicating the severity of tightness felt. If not reported, it should be `null`
* `knots` __should__ be reported for muscles only and __should__ be an integer (1-10) indicating the severity of discomfort caused by knots, tigger points, and musclular adhesions felt. If not reported, it should be `null`
* `ache` __should__ be an integer (1-10) indicating the severity of discomfort felt described as an ache, dull, or sore, indicating inflammation and muscle spasms are likely present. If not reported, it should be `null`
* `sharp` __should__ be an integer (1-10) indicating the severity of discomfort felt described as sharp, acute, shooting, indicating that inflammation and muscle spasms are likely present. If not reported, it should be `null`

Note: Fathom can customize the processing of symptoms data upon request to accommodate third-party systems that only report a subset of measures.

#### Optional Data Elements

The following data elements are not required to generate a plan using the  __Daily Readiness__ pathway, but enhance the customization of the plan for the athlete.

* `sessions` __should__ be a list of workout sessions completed but not yet submitted to Fathom.
* `sessions_planned` __should__ be a boolean representing whether the athlete plans to train again that day.

`session` __if present__, __should__ follow the requirements outlined in the  __Post-Workout__ pathway


### Post-Workout
#### Required Data Elements

The following data elements are required when following the  __Post-Workout__ pathway to __Daily Plan__ generation.  Sessions can either be logged manually be an athlete or transferred from a third party source such as Apple's HealthKit app.

* `session` __should__ include the data elements as specified below
* `sessions_planned` __should__ be a boolean representing whether the athlete plans to train again that day.

`session` data elements

* `event_date` __should__ be a Datetime and reflect the start time of the session
* `end_date` is __optional__ Datetime parameter that reflects the end time of the session from third party source
* `sport_name` __should__ be an integer reflecting SportName enumeration.
* `duration` __should__ be an integer and reflect the minutes duration which the athlete confirmed (third party source) or entered (manually logged session).
* `calories` __if present__, __should__ be an integer and represent the calorie information obtained from a third party source workout _(only needed for third party source workouts)_
* `distance` __if present__, __should__ be an integer and represent the distance information obtained from a third party source workout _(only needed for third party source workouts)_
* `source` __if present__, __should__ be 0 for manually logged session and 1 for a third party source workout
* `deleted` __if present__, __should__ be a boolean and true to delete the workout transferred from a third party source
* `ignored` __if present__, __should__ be a boolean and true for short walking workouts.  This is typically only used for sessions created by third-party apps that should be excluded from Fathom processing.
* `hr_data` __if present__, __should__ be the heart rate data associated with a third party source workout. Each hr will have `startDate` (Datetime), `endDate` (Datetime) and `value` (integer) _(only needed for third party source workouts)_
* `description` is __optional__ string parameter to provide a short description of the session they're adding
* `post-session-survey` __should__ follow requirements below

`post-session-survey` data elements

* `event_date` __should__ be a Datetime and reflect the local date and time when the survey (associated with the workout) was completed
* `RPE` __should__ be an integer between 1 and 10 indicating the  _Rating of Perceived Exertion_ of the athlete during the session
* `soreness` __should__ follow the same definition as in  _Daily Readiness_


### Symptom-Reporting
#### Required Data Elements
The following data elements are required when following the  __Symptom-Reporing__ pathway to __Daily Plan__ generation.

* `event_date` __should__ be a Datetime and reflect the local time that survey was taken
* `soreness` __should__ follow the same definition as in _Daily Readiness_


## Appendix

### Enumerations

#### Reportable body part

```
    chest = 2
    abdominals = 3
    groin = 5
    quads = 6
    knee = 7
    shin = 8
    ankle = 9
    foot = 10
    it_band = 11
    lower_back = 12
    glutes = 14
    hamstrings = 15
    calves = 16
    achilles = 17
    upper_back_neck = 18
    elbow = 19
    wrist = 20
    lats = 21
    biceps = 22
    triceps = 23
    forearm = 24
    it_band_lateral_knee = 27
    hip_flexor = 28
    deltoid = 29
```

#### All body parts
```
    shoulder = 1
    chest = 2
    abdominals = 3
    hip = 4
    groin = 5
    quads = 6
    knee = 7
    shin = 8
    ankle = 9
    foot = 10
    it_band = 11
    lower_back = 12
    general = 13
    glutes = 14
    hamstrings = 15
    calves = 16
    achilles = 17
    upper_back_neck = 18
    elbow = 19
    wrist = 20
    lats = 21
    biceps = 22
    triceps = 23
    forearm = 24
    core_stabilizers = 25
    erector_spinae = 26
    it_band_lateral_knee = 27
    hip_flexor = 28
    deltoid = 29
    deep_rotators_hip = 30
    obliques = 31

    # shin
    anterior_tibialis = 40
    peroneals_longus = 41

    # calves
    posterior_tibialis = 42
    soleus = 43
    gastrocnemius_medial = 44

    # hamstrings
    bicep_femoris_long_head = 45
    bicep_femoris_short_head = 46
    semimembranosus = 47
    semitendinosus = 48

    # groin
    adductor_longus = 49
    adductor_magnus_anterior_fibers = 50
    adductor_magnus_posterior_fibers = 51
    adductor_brevis = 52
    gracilis = 53
    pectineus = 54

    # quads
    vastus_lateralis = 55
    vastus_medialis = 56
    vastus_intermedius = 57
    rectus_femoris = 58

    tensor_fascia_latae = 59 # hips
    piriformis = 60 # deep rotator of hip

    gastrocnemius_lateral = 61  # calves - was 75 but that was a duplicate
    sartorius = 62  # quads

    # glutes
    gluteus_medius_anterior_fibers = 63
    gluteus_medius_posterior_fibers = 64
    gluteus_minimus = 65
    gluteus_maximus = 66

    # deep rotators of the hip (30)
    quadratus_femoris = 67

    # knee
    popliteus = 68

    external_obliques = 69  # abdominal

    # lower_back
    quadratus_lumorum = 70

    # hip_flexor
    psoas = 71
    iliacus = 72

    # core_stabilizers
    transverse_abdominis = 73
    internal_obliques = 74

    # abdominals
    rectus_abdominis = 75

    # upper back, traps, neck
    upper_trapezius = 76
    levator_scapulae = 77
    middle_trapezius = 78
    lower_trapezius = 79
    rhomboids = 80

    # chest
    pectoralis_minor = 81
    pectoralis_major = 82

    # deltoid (29)
    anterior_deltoid = 83
    medial_deltoid = 84
    posterior_deltoid = 85

    upper_body = 91
    lower_body = 92
    full_body = 93

    # merge
    semimembranosus_semitendinosus = 100
    anterior_adductors = 101
    rectus_femoris_vastus_intermedius = 102
    glute_med = 103
    upper_traps_levator_scapulae = 105
    middle_traps_rhomboids = 106
    pec_major_minor = 107
    hip_flexor_merge = 108
```

#### side

```
    none_unilateral = 0
    left = 1
    right = 2
```


#### sport name
```
    basketball = 0
    baseball = 1
    softball = 2
    cycling = 3
    field_hockey = 4
    football = 5
    general_fitness = 6
    golf = 7
    gymnastics = 8
    skate_sports = 9
    lacrosse = 10
    rowing = 11
    rugby = 12
    diving = 13
    soccer = 14
    pool_sports = 15
    tennis = 16
    distance_running = 17
    sprints = 18
    jumps = 19
    throws = 20
    volleyball = 21
    wrestling = 22
    weightlifting = 23
    track_field = 24
    archery = 25
    australian_football = 26
    badminton = 27
    bowling = 28
    boxing = 29
    cricket = 30
    curling = 31
    dance = 32
    equestrian_sports = 33
    fencing = 34
    fishing = 35
    handball = 36
    hockey = 37
    martial_arts = 38
    paddle_sports = 39
    racquetball = 40
    sailing = 41
    snow_sports = 42
    squash = 43
    surfing_sports = 44
    swimming = 45
    table_tennis = 46
    water_polo = 47
    cross_country_skiing = 48
    downhill_skiing = 49
    kick_boxing = 50
    snowboarding = 51
    endurance = 52
    power = 53
    speed_agility = 54
    strength = 55
    cross_training = 56
    elliptical = 57
    functional_strength_training = 58
    hiking = 59
    hunting = 60
    mind_and_body = 61
    play = 62
    preparation_and_recovery = 63
    stair_climbing = 64
    traditional_strength_training = 65
    walking = 66
    water_fitness = 67
    yoga = 68
    barre = 69
    core_training = 70
    flexibility = 71
    high_intensity_interval_training = 72
    jump_rope = 73
    pilates = 74
    stairs = 75
    step_training = 76
    wheelchair_walk_pace = 77
    wheelchair_run_pace = 78
    taichi = 79
    mixed_cardio = 80
    hand_cycling = 81
    climbing = 82
    other = 83
```

