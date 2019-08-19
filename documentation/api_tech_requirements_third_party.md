# FathomAI - Plans API (v 4.4.0)
## Technical Summary


### Overview

This technical summary provides prospective third party partners ('providers') of  __Fathom's Plans API__ with a brief summary of the data returned from the service along with the technical and data requirements.  This document is not a substitute for the full API specification.

### Daily Plan

The plans service generates a __Daily Plan__ for an athlete based on one or both of the following data elements:

* __Daily Readiness__ - information about the athlete's "readiness" and pain/soreness for a given day
* __Post-Workout__ - information about a athlete's workout session along with their RPE and pain/soreness following the workout

A __Daily Plan__ can be created with as little as one of the above data elements; however, as this information is gathered over time, Fathom's analytics will also use historical patterns in pain/soreness and workouts to influence __Daily Plan__ creation.



A __Daily Plan__ provides a personalized, research-driven recovery plan for an athlete.  A plan may consist of one or more modalities, targeting one or more recovery goals Fathom analytics identifies for the athlete.

Modalities such as __Active Rest (Before Training)__, __Active Rest (After Training)__, and __Cooldown__ include a series of recommended exercises personalized for the athlete that day.  These exercises are provided in a sequence consistent with sports science research.
 
Other modalities do not include exercises but are assigned to a plan based on athlete needs.  These modalities include __heat__, __ice__ and __cold water immersion__.

Recommended dosages are also provided for each exercise and modality.  These dosages are associated with three different active times for the entire exercise sequence (__Efficient__, __Complete__, __Comprehensive__), depending upon the time the athlete has available.  Dosages are also provided by goal, allowing the athlete to further customize their recovery.


## Technical and Data Requirements

### Terminology

The terminology of [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt) (specifically __must__, __should__, __may__ and their negatives) applies.  The word __will__, when applied to the Plans API ("the API"), has the same meaning as __must__.

Each third-party partner will be recognised as a "provider" and will be assigned a unique 'Provider Code'.  This __will__ be a string matching the regular expression `^[a-z][a-z0-9\-]{3,31}$`.

### Protocol

The API supports communication over HTTPS only.  The client __must__ recognise the Amazon Trust Services LLC certificate root. 

### Encoding

The API supports communication using JSON encoding only.  The client __must__ submit the headers `Content-Type: application/json` and `Accept: application/json` (or a subtype `application/{subtype}+json`, if appropriate) for all requests.  Failure to do so __will__ result in a `415 Unsupported Media Type` response.  The API __will__ include the header `Content-Type: application/json` (or a subtype if appropriate) with its response.

### Authentication

Unless otherwise specified, the endpoints in the API are authenticated by a JWT bearer token.  The client __must__ submit the header `Authorization: <JWT>` with all requests. Failure to do so, or submitting an invalid or expired JWT, __will__ result in a `401 Unauthorized` response.  

It is expected that partners will normally generate and sign their own JWTs for their clients, providing appropriate authorisation for each user in accordance with their business and compliance requirements.

#### Signing keys

Prior to integrating with the API, each partner __must__ supply a set of one or more public keys with which they will sign clients' JWT credentials.  This __must__ take the form of an [RFC 7517](https://tools.ietf.org/html/rfc7517) JSON Web Key Set document, for example:

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

Each key within the key set __must__ have a `kid` field matching the regular expression `^([a-z][a-z0-9\-]{3,31})_([a-z0-9\-]+)$`, where the first group of the expression is the partner's Provider Code.  

Each key within the key set __must__ have a `use` field set to `sig` if the key is to be used for signing JWTs.  Partners __should not__ include keys with other values in the key set.

At the present time the only algorithm from the [RFC 7518](https://tools.ietf.org/html/rfc7518#section-3) list supported is RSA-256, so the value of the `alg` field for each key in the key set __must__ be `RS256`.  We hope to support at least `ES256` in the near future.

Partners __may__ include the non-standardised fields `_nbf` and `_exp` in key definitions; if these fields are provided, they __must__ follow the semantics of the corresponding JWT claim fields in [RFC7519](https://tools.ietf.org/html/rfc7519#section-4.1.3), and the API __will__ interpret them similarly (that is to say, a JWT with an `iat` value falling before the corresponding key's `nbf` value or after its `exp` value, will not be considered valid).  This allows partners to perform key rotation in an orderly fashion.

Partners __may__ include the non-standardised field `_env` in key definitions; if this field is provided the value __must__ be a String matching the regular expression `^[a-z0-9]+$` or an array of such Strings, and the API __will__ interpret this as a list of the environments where the key should be accepted.  This allows partners to use different signing keys for production and non-production environments.

#### JWT claims

The JWTs provided by clients __must__ contain the following claims:

* `iss`, which __must__ be a String matching the regular expression `^([a-z][a-z0-9\-]{3,31})_([a-z0-9\-]+)$`, where the first group of the expression is the partner's Provider Code.  
* `aud`, which __must__ be a String matching the regular expression `^fathom(_[a-z0-9]+)?$` (or an array containing such a String).  If the group is provided (eg `fathom_production`), the API __will__ treat the second part as an environment specifier, and __will__ only accept as valid JWTs targeted at its own environment (for instance, the production API will only accept tokens with an `aud` value of `fathom` and/or `fathom_production`).
* `iat` __must__ be specified.
* `exp` __must__ be specified.  The total period of validity of the JWT (ie the time range between the lesser of `iat` and `nfb`, and `exp`) __must not__ be greater than 86400 seconds.
* `sub`, which __must__ be a Uuid identifying the user on whose behalf the client is acting.  In general the API will only allow requests which correspond to actions affecting this user.
* `scope`, which __must__ be a String containing a space-separated list of Scopes, where each Scope is a String matching the regular expression `^[a-z][a-z0-9\.:]*$`.  The following scopes are recognised by the API:
   * `fathom.plans:read`: provides access to read-only functionality for the user identified by the `sub` claim
   * `fathom.plans:write`: provides access to write functionality for the user identified by the `sub` claim.  This is a superset of `fathom.plans:read`.
   * `fathom.plans:service`: provides access to all functionality for all users.  JWTs with this scope are subject to additional validation conditions described below.

#### Service tokens

Partners __may__ interact with the API on a business-to-business basis instead of, or in addition to, building clients which allow users to interact with the API directly.  Partners' private servers __may__ authenticate such requests using a JWT carrying the `fathom.plans:service` scope.  Such tokens must meet the following additional validation conditions:

* The value of the `sub` field __must__ be the String `00000000-0000-4000-8000-000000000000`.
* The total period of validity of the JWT __must not__ be greater than 600 seconds.

### General responses

In addition to the API responses and the specific responses for each endpoint, the server __may__ respond with one of the following HTTP responses:

* `400 Bad Request` with `Status` header equal to `InvalidSchema`, if the JSON body of the request does not match the requirements of the endpoint.
* `403 Forbidden` with `Status` header equal to `Forbidden`, if the user is not allowed to perform the requested action.
* `404 Unknown` with `Status` header equal to `UnknownEndpoint`, if an invalid endpoint was requested.

## Schema

### Simple

The following simple types __may__ be used in responses:

* `string`, `number`: as defined in the [JSON Schema](http://json-schema.org) standard.
* `Uuid`: a `string` matching the regular expression `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`, that is, the string representation of an [RFC 4122](https://tools.ietf.org/html/rfc4122) UUID.
* `Datetime`: a `string` matching the regular expression `/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|+\d{2}:\d{2})/` and representing a date and time in full [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) format.

### Daily Readiness

#### Required Data Elements

The following data elements are required when following the __Daily Readiness__ pathway to __Daily Plan__ generation.

* `date_time` __should__ reflect the local time that survey was taken
* `soreness` __should__ reflect a list of body parts(`sore_part`) with pain or soreness. Length __could__ be 0.

`sore_part` __should__ include the following:

* `body_part` __should__ be an integer reflecting BodyPart enum of the body part with pain/soreness
* `severity` __should__ be an integer 0, 1, 3 or 5 indicating the severity of the pain/soreness
* `movement` __should__ be an integer 0, 1, 3 or 5 indicating how much movement is restricted 
* `side` __should__ be an integer, either 0 (both sides/non-bilateral), 1 (left) or 2 (right)
* `pain` __should__ be a boolean to indicate whether it's pain or soreness.

Note: Fathom can customize the processing of `severity` and `movement` data upon request to accommodate third-party systems that only report `severity` related measures.

#### Optional Data Elements

The following data elements are not required to generate a plan using the __Daily Readiness__ pathway, but enhance the customization of the plan for the athlete.

* `sleep_quality` __should__ be an integer between 1 and 10 or null
* `readiness` __should__ be an integer between 1 and 10 or null
* `sessions` __should__ be a list of workout sessions completed but not yet submitted to Fathom.
* `sleep_data` __should__ be a list of sleep_events.
* `sessions_planned` __should__ be a boolean representing whether the athlete plans to train again that day.
* `health_sync_date` is __optional__ and only provided if one of the sessions is obtained from Apple's HealthKit app

`session` __if present__, __should__ follow the requirements outlined in the __Post-Workout__ pathway


`sleep_event` __if present__, __should__ include the following:

* `start_date` __should__ indicate the date/time start of sleep/in bed
* `end_date` __should__ indicate the date/time end of sleep/in bed


### Post-Workout
#### Required Data Elements

The following data elements are required when following the __Post-Workout__ pathway to __Daily Plan__ generation.

* `health_sync_date` is __optional__ and only provided if one of the sessions is obtained from Apple's HealthKit  app
* `session` __should__ include the data elements as specified below
* `sessions_planned` __should__ be a boolean representing whether the athlete plans to train again that day.

`session` data elements

* `event_date` __should__ reflect the start time of the session (Apple HealthKit data) or default date (manually logged session)
* `end_date` is __optional__ parameter that reflects the end time of the session for health data
* `session_type` __should__ be an integer reflecting SessionType enumeration.
* `sport_name` __should__ be an integer reflecting SportName enumeration.
* `duration` __should__ be in minutes and reflect the duration which the athlete confirmed (health data) or entered (manually logged session).
* `calories` __if present__, __should__ be calorie information obtained from health workout _(only needed for health workout)_
* `distance` __if present__, __should__ be distance information obtained from health workout _(only needed for health workout)_
* `source` __if present__, __should__ be 0 for manually logged session and 1 for health data
* `deleted` __if present__, __should__ be true if the athlete deletes the workout detected from Apple's HealthKit app
* `ignored` __if present__, __should__ be true for short walking workouts.
* `hr_data` __if present__, __should__ be the heart rate data associated with the health workout. each hr will have `startDate`, `endDate` and `value` _(only needed for health workout)_
* `description` is __optional__ parameter to provide short description of the session they're adding
* `post-session-survey` __should__ follow requirements below

`post-session-survey` data elements

* `event_date` __should__ reflect the local date and time when the survey (associated with the workout) was completed
* `RPE` __should__ be an integer between 1 and 10 indicating the _Rate of Perceived Exertion_ of the athlete during the session
* `soreness` __should__ follow the same definition as in _Daily Readiness_





