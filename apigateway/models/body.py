from models.soreness_base import BodyPartLocation
from models.body_parts import BodyPart, BodyPartFactory


class Body(object):
    def __init__(self):
        self.body_parts = {}
        self.inverse_synergists = {}
        self.inverse_agonists = {}
        self.inverse_antagonists = {}

        self.load_body_parts()

    def load_body_parts(self):

        body_part_factory = BodyPartFactory()

        for b in range(1, 27):
            if b != 13:
                body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(b), None))
                self.body_parts[b] = body_part
                for s in body_part.synergists:
                    if s not in self.inverse_synergists:
                        self.inverse_synergists[s] = set()
                    self.inverse_synergists[s].add(b)

                for a in body_part.agonists:
                    if a not in self.inverse_agonists:
                        self.inverse_agonists[a] = set()
                    self.inverse_agonists[a].add(b)

                if body_part_factory.is_joint(body_part):
                    for a in body_part.antagonists:
                        if a not in self.inverse_antagonists:
                            self.inverse_antagonists[a] = set()
                        self.inverse_antagonists[a].add(b)

    def mark_tight(self, body_part_enum):

        self.body_parts[body_part_enum].tight_count += 1

        for a in self.body_parts[body_part_enum].antagonists:
            self.body_parts[a].underactive_risk_count += 1
            for s in self.body_parts[a].synergists:
                self.body_parts[s].overactive_risk_count += 1

    def mark_pain(self, body_part_enum):

        body_part_factory = BodyPartFactory()

        pain_part = BodyPart(BodyPartLocation(body_part_enum), None)

        if body_part_factory.is_joint(pain_part):
            for s in self.body_parts[body_part_enum].stabilizers:
                self.body_parts[s].tight_risk_count += 1
                self.body_parts[s].overactive_risk_count += 1
            for a in self.body_parts[body_part_enum].agonists:
                self.body_parts[a].weakness_count += 1
            for a in self.body_parts[body_part_enum].antagonists:
                self.body_parts[a].weakness_count += 1
        else:
            for a in self.body_parts[body_part_enum].antagonists:
                self.body_parts[a].weakness_count += 1

        for i in self.inverse_synergists[body_part_enum]:
            self.body_parts[i].possible_soreness_source_count += 1

        for i in self.inverse_agonists[body_part_enum]:
            self.body_parts[i].possible_soreness_source_count += 1

    def mark_sore(self, body_part_enum):

        self.body_parts[body_part_enum].overactive_count += 1

        for a in self.body_parts[body_part_enum].antagonists:
            self.body_parts[a].weakness_count += 1

        for i in self.inverse_synergists[body_part_enum]:
            self.body_parts[i].possible_soreness_source_count += 1

        for i in self.inverse_agonists[body_part_enum]:
            self.body_parts[i].possible_soreness_source_count += 1



