from serialisable import Serialisable


class TimeBlockAsymmetry(Serialisable):
    def __init__(self, time_block, left, right, significant):
        self.left = left
        self.right = right
        self.time_block = time_block
        self.significant = significant

    def json_serialise(self):
        ret = {
            'left': self.left,
            'right': self.right,
            'time_block': self.time_block,
            'significant': self.significant
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        time_block = input_dict.get('time_block', 0) if input_dict.get('time_block') is not None else 0
        left = input_dict.get('left', 0) if input_dict.get('left') is not None else 0
        right = input_dict.get('right', 0) if input_dict.get('right') is not None else 0
        significant = input_dict.get('significant', False) if input_dict.get('time_block') is not None else False

        asymmetry = cls(time_block, left, right, significant)

        return asymmetry


class SessionAsymmetry(Serialisable):
    def __init__(self, session_id):
        self.session_id = session_id
        self.time_blocks = []

    def json_serialise(self):
        ret = {
            'session_id': self.session_id,
            'time_blocks': [t.json_serialise() for t in self.time_blocks]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        session = cls(session_id=input_dict['session_id'])
        session.time_blocks = [TimeBlockAsymmetry.json_deserialise(tb) for tb in input_dict.get('time_blocks', [])]

        return session