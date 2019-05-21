
class TrendsData(object):
    def __init__(self, trigger):
        self.trigger = trigger

    def data(self):
        visualizations = {
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
                        'color': 2,
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
        return visualizations[self.trigger]
