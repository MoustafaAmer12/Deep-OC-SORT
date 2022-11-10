"""Generic detector."""
import os
import pickle

import torch

from external.adaptors import yolox_adaptor


class Detector(torch.nn.Module):
    K_MODELS = {"yolox": "external/weights/bytetrack_ablation.pth.tar"}

    def __init__(self, model_type, path=None):
        super().__init__()
        if model_type not in self.K_MODELS:
            raise RuntimeError(f"{model_type} detector not supported")
        if path is None:
            path = self.K_MODELS[model_type]
        self.model_type = model_type
        self.path = path
        self.model = None

        os.makedirs("./cache", exist_ok=True)
        self.cache_path = os.path.join(
            "./cache", f"det_{os.path.basename(path).split('.')[0]}.pkl"
        )
        self.cache = {}
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "rb") as fp:
                self.cache = pickle.load(fp)
        else:
            self.initialize_model()

    def initialize_model(self):
        """Wait until needed."""
        if self.model_type == "yolox":
            self.model = yolox_adaptor.get_model(self.path)
        self.model.eval()

    def forward(self, batch, tag=None):
        if tag in self.cache:
            return self.cache[tag]
        elif self.model is None:
            self.initialize_model()

        with torch.no_grad():
            output = self.model(batch)
        if tag is not None:
            self.cache[tag] = output.cpu()

        return output

    def dump_cache(self):
        with open(self.cache_path, "wb") as fp:
            pickle.dump(self.cache, fp)
