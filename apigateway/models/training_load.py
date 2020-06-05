from models.training_volume import StandardErrorRange


class TrainingLoad(object):
    def __init__(self):
        self.tissue_load = None
        self.force_load = None
        self.power_load = None

    def add_tissue_load(self, tissue_load):
        if self.tissue_load is None:
            self.tissue_load = StandardErrorRange(observed_value=0)
        if tissue_load is not None:
            self.tissue_load.add(tissue_load)

    def add_force_load(self, force_load):
        if self.force_load is None:
            self.force_load = StandardErrorRange(observed_value=0)
        if force_load is not None:
            self.force_load.add(force_load)

    def add_power_load(self, power_load):
        if self.power_load is None:
            self.power_load = StandardErrorRange(observed_value=0)
        if power_load is not None:
            self.power_load.add(power_load)
