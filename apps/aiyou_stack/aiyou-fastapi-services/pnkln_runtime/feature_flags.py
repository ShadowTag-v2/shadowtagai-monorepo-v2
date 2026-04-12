import pathlib

import yaml


class PnklnFlags:
    def __init__(self, path="pnkln_config/feature_flags.yaml"):
        self.path = pathlib.Path(path)
        self.data = {"flags": {}}
        if self.path.exists():
            self.data = yaml.safe_load(self.path.read_text())

    def get(self, key, default=False):
        return self.data.get("flags", {}).get(key, default)


FLAGS = PnklnFlags()
