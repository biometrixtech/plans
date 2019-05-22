import json
import os

script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'triggers.json')
with open(file_path, 'r') as f:
    triggers = json.load(f)['triggers']


class TriggerData(object):
    def __init__(self):
        self.triggers = triggers
        self.visualization_data = {
            1: {
                'title': "",
                'y_axis_1': "Training Volume",
                'y_axis_2': "",
                'legend': [
                    {
                        'color': 0,
                        'text': "",
                        'type': 0
                    }
                ]
            },
            2: {
                'title': "",
                'y_axis_1': "Training Volume",
                'y_axis_2': "",
                'legend': [
                    {
                        'color': 0,
                        'text': "High load days",
                        'type': 0
                    }
                ]
            },
            3: {
                'title': "",
                'y_axis_1': "Training Volume",
                'y_axis_2': "Severity",
                'legend': [
                    {
                        'color': 2,
                        'text': "Pain severity",
                        'type': 0
                    },
                    {
                        'color': 1,
                        'text': "Soreness severity",
                        'type': 0
                    }
                ]
            },
            4: {
                'title': "",
                'y_axis_1': "Training Volume",
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
                'y_axis_1': "Training Volume",
                'y_axis_2': "Severity",
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
                'y_axis_1': "Training Volume",
                'y_axis_2': "Movement Quality",
                'legend': [
                ]
            },

        }

    def get_visualization_data(self, trigger):
        visualizations = self.visualization_data
        return visualizations[trigger]

    def get_trigger_data(self, trigger):
        triggers = self.triggers
        return triggers[str(trigger)]
