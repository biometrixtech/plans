import athlete
import soreness_and_injury
import training
import datetime
import session


'''
academy schedule: M,W,F - 90 minutes
strength and conditioning coach - wed am for 1 hr
games: tournaments on weekends, but not every weekend
this sat/sun she DOES have a tournament
s and c - activity type: 1 hr of interval training

TBD: more than one practice / day, differing lengths of practice, start time?

{Kit setup}

{UI may not show here Mon/Tues, she will be signing up after her strength and conditioning; not sure if she'll
tell us about the strength and conditioning}

{finishes onboarding}


WE CREATE A PLAN!

PLAN:
W {WE DONT HAVE SEQUENCE}
PRACTICE - 90 MIN
S& C - 60 MIN
Long-Term Recovery (expires fri noon) {some modalities are only EOD, others are throughout the day,
    up to 2-4 x day for 48 hrs }
 -- has two distinct contexts: interventions after day's sessions are done (pretty much icing), generally repeated throughout the day
 (low resource)
 -- a fourth category is short-term: should be done immediately after practice

 --> she clicks on recovery ...
exercises addressing knee soreness and potentially her chronic right ankle sprains
how many does she see? need to have all four phases present (inhibit, lengthen, etc.)
goal and focus text appears (e.g., why are we doing this); set information (duration, dosage, how often should I do these?)
how many times should she do this in the next 48 hours? {TBD from Amina}
she can track how many times she does it

--> she goes back to plan, doesn't do any of exercises, clicks on S&C, says "log it" (she completed), she goes into post-
session survey, get activity, get RPE, get duration, doesn't report any post-session injury because her knee is always
sore

[if soreness she reported was a 3 or higher, in a subsequent post-session survey we would ask about whether that soreness affected her]
[if report for 3 consecutive days, that we would have followed up on but on day 0 so no biggie]

[Note: for strength and conditioning we don't ask her if she had sensors, but if this was a diff type, she would be asked
why she didn't wear her sensors]

RPE = 8, 60 minutes
--> triggers nutrition, hydration (otherwisewould have gotten this on firday pre-tournament)
--> triggers a change in a distribution of time spent in modalities (inhibit); timestamp of recovery is updated, "is new indicator" along with a "why"

should recovery be a queue (with times, etc)?

"come back after your session"...




 [the need to hydrate and nutrition would be triggered on Friday AM through a nightly process]




but she does tell us about s and c, enters an RPE,



'''


def create_athlete():

    todays_date = datetime.date(2018, 6, 27)

    test_athlete = athlete.YouthAthlete()
    test_athlete.full_name = "Rachel Murray"
    test_athlete.email = "rachel.murray@fathomai.com"
    test_athlete.date_of_birth = datetime.date(2002, 3, 26)
    test_athlete.height = 65    # this correct?
    test_athlete.weight = 130   # lbs

    sport1 = athlete.Sport()
    sport1.name = athlete.SportName.soccer
    sport1.level = athlete.SportLevel.club_travel   # position: left-striker
    sport1.season_start_date = datetime.datetime(2018,1,1)
    sport1.season_end_date = datetime.date(2018,8,31)

    sport2 = athlete.Sport()
    sport2.name = athlete.SportName.soccer
    sport2.level = athlete.SportLevel.high_school   # position: right-defend
    sport2.season_start_date = datetime.datetime(2018, 8, 1)
    sport2.season_end_date = datetime.date(2018, 11, 30)

    typical_schedule = session.Schedule()
    practice1 = session.PracticeSession()
    practice1.duration_minutes = 90
    practice1.day_of_week = session.DayOfWeek.monday

    practice2 = session.PracticeSession()
    practice2.day_of_week = session.DayOfWeek.wednesday
    practice2.duration_minutes = 90

    practice3 = session.PracticeSession()
    practice3.day_of_week = session.DayOfWeek.friday
    practice3.duration_minutes = 90

    s_and_c = session.StrengthConditioningSession()
    s_and_c.day_of_week = session.DayOfWeek.wednesday
    s_and_c.duration_minutes = 60

    typical_schedule.sessions.append(practice1)
    typical_schedule.sessions.append(practice2)
    typical_schedule.sessions.append(practice3)
    typical_schedule.sessions.append(s_and_c)

    sport1.typical_schedule = typical_schedule

    test_athlete.sports.append(sport1)
    test_athlete.sports.append(sport2)

    test_athlete.injury_status = soreness_and_injury.InjuryStatus.healthy_chronically_injured

    injury1 = soreness_and_injury.Injury()
    injury1.body_part = soreness_and_injury.BodyPartLocation.ankle
    injury1.injury_type = soreness_and_injury.InjuryType.ligament
    injury1.injury_descriptor = soreness_and_injury.InjuryDescriptor.sprain
    injury1.date = datetime.date(2017, 10, 1)
    injury1.days_missed = soreness_and_injury.DaysMissedDueToInjury.less_than_7_days

    injury2 = soreness_and_injury.Injury()
    injury2.body_part = soreness_and_injury.BodyPartLocation.ankle
    injury2.injury_type = soreness_and_injury.InjuryType.ligament
    injury2.injury_descriptor = soreness_and_injury.InjuryDescriptor.sprain
    injury2.date = datetime.date(2018, 3, 1)
    injury2.days_missed = soreness_and_injury.DaysMissedDueToInjury.less_than_7_days

    test_athlete.injury_history.append(injury1)
    test_athlete.injury_history.append(injury2)

    daily_readiness_survey = soreness_and_injury.DailyReadinessSurvey()
    daily_readiness_survey.readiness = 4
    daily_readiness_survey.sleep_quality = 6
    daily_readiness_survey.date = todays_date

    daily_soreness = soreness_and_injury.DailySoreness()
    daily_soreness.body_part = soreness_and_injury.BodyPartLocation.knee
    daily_soreness.type = soreness_and_injury.SorenessType.joint_related
    daily_soreness.severity = soreness_and_injury.JointSorenessSeverity.dull_ache

    daily_readiness_survey.soreness.append(daily_soreness)



