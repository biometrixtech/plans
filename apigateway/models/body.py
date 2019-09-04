from models.soreness_base import BodyPartLocation
from models.body_parts import BodyPart, BodyPartFactory


class Body(object):
    def __init__(self):
        self.body_parts = {}

        self.load_body_parts()

    def load_body_parts(self):

        body_part_factory = BodyPartFactory()

        for b in range(0, 27):
            body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(b), None))
            self.body_parts[b] = body_part

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
                self.body_parts[a].weak_count += 1
            for a in self.body_parts[body_part_enum].antagonists:
                self.body_parts[a].weak_count += 1
        else:
            for a in self.body_parts[body_part_enum].antagonists:
                self.body_parts[a].weak_count += 1

    def mark_sore(self, body_part_enum):

        self.body_parts[body_part_enum].overactive_count += 1

        for a in self.body_parts[body_part_enum].antagonists:
            self.body_parts[a].weak_count += 1




