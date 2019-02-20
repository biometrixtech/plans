const coachesDashboardCardsData = isToday => {
    if(isToday) {
        return [
            {
                description: 'Significant pain or soreness reported: consult medical staff, consider not training',
                label:       'SEEK MED EVAL TO CLEAR FOR TRAINING',
                overlayText: 'When an athlete completes a survey, their status will update here.',
                value:       'seek_med_eval_to_clear_for_training',
            },
            {
                description: 'Modify intensity, movements & drills to prevent severe pain & soreness from worsening',
                label:       'ADAPT TRAINING TO AVOID SYMPTOMS',
                value:       'adapt_training_to_avoid_symptoms',
            },
            {
                description: 'Modify training if pain increases. Prioritize recovery to prevent development of injury',
                label:       'MONITOR, MODIFY IF NEEDED',
                value:       'monitor_modify_if_needed',
            },
            {
                description: 'Shorten training or limit intensity & to help facilitate recovery from spike in load',
                label:       'RECOVERY DAY RECOMMENDED',
                value:       'recovery_day_recommended',
            },
            {
                description: 'Survey responces indicate ready to train as normal if no other medical limitations.',
                label:       'READY TO TRAIN BASED ON DATA',
                value:       'all_good',
            },
        ]
    }
    return [
        {
            description: 'Significant pain or soreness reported: consult medical staff, consider not training',
            label:       'SEEK MED EVAL TO CLEAR FOR TRAINING',
            overlayText: 'When an athlete has been identified as having a chronic issue, their status will update here.',
            value:       'seek_med_eval_to_clear_for_training',
        },
        {
            description: 'Modify intensity, movements & drills to avoid aggravating areas of severe pain & soreness',
            label:       'AT RISK OF TIME-LOSS INJURY',
            value:       'at_risk_of_time_loss_injury',
        },
        {
            description: 'Consider decreasing workload this week or prioritizing holistic recovery',
            label:       'AT RISK OF OVERTRAINING',
            value:       'at_risk_of_overtraining',
        },
        {
            description: 'Increase variety in training duration & intensity, prioritize holistic recovery',
            label:       'LOW VARIABILITY INHIBITING RECOVERY',
            value:       'low_variability_inhibiting_recovery',
        },
        {
            description: 'Unless tapering, increase load with longer or higher intensity session or supplemental session',
            label:       'AT RISK OF UNDERTRAINING',
            value:       'at_risk_of_undertraining',
        },
    ]
};

const coachesDashboardSortBy = [
    {
        label: 'VIEW ALL',
        value: 'view_all',
    },
    {
        label: 'CLEARED TO TRAIN',
        value: 'cleared_to_play',
    },
    {
        label: 'NOT CLEARED TO TRAIN',
        value: 'not_cleared_to_play',
    },
];