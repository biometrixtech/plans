import json
import os

script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'triggers.json')
with open(file_path, 'r') as f:
    triggers = json.load(f)['triggers']
visualization_data = {
            1: {
                'title': "",
                'y_axis_1': "Relative Load",
                'y_axis_2': "",
                'legend': [
                    {
                        'color': 3,
                        'text': "Relative Load",
                        'type': 0
                    }
                ]
            },
            2: {
                'title': "",
                'y_axis_1': "Relative Load",
                'y_axis_2': "",
                'legend': [
                    {
                        'color': 0,
                        'text': "High training loads",
                        'type': 0
                    }
                ]
            },
            3: {
                'title': "",
                'y_axis_1': "Relative Load",
                'y_axis_2': "Severity",
                'legend': [
                    {
                        'color': 2,
                        'text': "{bodypart} pain severity",
                        'type': 0
                    },
                    {
                        'color': 1,
                        'text': "{bodypart} soreness severity",
                        'type': 0
                    }
                ]
            },
            4: {
                'title': "",
                'y_axis_1': "Relative Load",
                'y_axis_2': "Severity",
                'legend': [
                    {
                        'color': 1,
                        'text': "Soreness severity",
                        'type': 0
                    },
                    {
                        'color': 1,
                        'text': "Projected duration of soreness without Recovery",
                        'type': 2
                    }
                ]
            },
            5: {
                'title': "",
                'y_axis_1': "Relative Load",
                'y_axis_2': "Efficiency",
                'legend': [
                    {
                        'color': 0,
                        'text': "Normal",
                        'type': 0
                    },
                    {
                        'color': 1,
                        'text': "Moderate",
                        'type': 0
                    },
                    {
                        'color': 2,
                        'text': "High risk",
                        'type': 0
                    }
                ]
            },
            6: {
                'title': "",
                'y_axis_1': "Relative Load",
                'y_axis_2': "Movement Quality",
                'legend': [
                ]
            },
            7: {
                'title': "",
                'y_axis_1': "Severity",
                'y_axis_2': "",
                'legend': [
                    {
                        'color': 6,
                        'text': "pain",
                        'type': 0
                    },
                    {
                        'color': 5,
                        'text': "soreness",
                        'type': 0
                    }
                ]
            },
            8: {
                'title': "",
                'y_axis_1': "Volume of Load",
                'y_axis_2': "",
                'legend': [
                    {
                        'color': 4,
                        'text': "Workload",
                        'type': 3
                    }
                ]
            }
        }

cta_data = {
    'heat': {
        'header': {
            'stress': "",
            'response': "Heat",
            'biomechanics': "Heat"
        },
        'benefit': {
            'stress': "",
            'response': "to optimize tissue mobility",
            'biomechanics': "to optimize tissue mobility"
        },
        'proximity': {
            'stress': "",
            'response': "within 30 min of training",
            'biomechanics': "within 30 min of training"
        }
    },
    'warm_up': {
        'header': {
            'stress': "",
            'response': "",
            'biomechanics': "Warm Up"
        },
        'benefit': {
            'stress': "",
            'response': "",
            'biomechanics': "for ideal movement prep"
        },
        'proximity': {
            'stress': "",
            'response': "",
            'biomechanics': "immediately before training"
        }
    },
    'active_recovery': {
        'header': {
            'stress': "Active Recovery",
            'response': "",
            'biomechanics': ""
        },
        'benefit': {
            'stress': "to mitigate DOMS severity",
            'response': "",
            'biomechanics': ""
        },
        'proximity': {
            'stress': "within 6 hrs of training",
            'response': "",
            'biomechanics': ""
        }
    },
    'mobilize': {
        'header': {
            'stress': "Mobilize",
            'response': "Mobilize",
            'biomechanics': "Mobilize"
        },
        'benefit': {
            'stress': "to expedite tissue healing",
            'response': "to expedite tissue healing",
            'biomechanics': "for injury prevention"
        },
        'proximity': {
            'stress': "after training",
            'response': "up to 3 times a day",
            'biomechanics': "3 times a week"
        }
    },
    'ice': {
        'header': {
            'stress': "Ice",
            'response': "Ice",
            'biomechanics': ""
        },
        'benefit': {
            'stress': "to reduce inflamation",
            'response': "to reduce inflamation",
            'biomechanics': ""
        },
        'proximity': {
            'stress': "after all training is complete",
            'response': "after all training is complete",
            'biomechanics': ""
        }
    },
    'cwi': {
        'header': {
            'stress': "",
            'response': "Cold Water Bath",
            'biomechanics': "Cold Water Bath"
        },
        'benefit': {
            'stress': "",
            'response': "to reduce muscle damage",
            'biomechanics': "to reduce muscle damage"
        },
        'proximity': {
            'stress': "",
            'response': "after all training is complete",
            'biomechanics': "after all training is complete"
        }
    },
}


class TriggerData(object):
    def __init__(self):
        self.triggers = triggers
        self.visualization_data = visualization_data
        self.cta_data = cta_data

    def get_visualization_data(self, trigger):
        return self.visualization_data[trigger]

    def get_trigger_data(self, trigger):
        return self.triggers[str(trigger)]

    def get_cta_data(self, activity_type):
        return self.cta_data[activity_type]
