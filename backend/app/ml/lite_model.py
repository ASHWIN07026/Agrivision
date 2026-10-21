from threading import Lock
import numpy as np
from ai_edge_litert.interpreter import Interpreter

class LiteDiseaseModel:
    def __init__(self, path):
        self.interpreter = Interpreter(model_path=str(path), num_threads=1)
        self.interpreter.allocate_tensors()
        self.input = self.interpreter.get_input_details()[0]
        self.output = self.interpreter.get_output_details()[0]
        self.output_shape = tuple(self.output["shape"])
        self.lock = Lock()

    def predict(self, values, verbose=0):
        values = np.asarray(values, dtype=self.input["dtype"])
        if tuple(values.shape) != tuple(self.input["shape"]):
            raise ValueError("Incorrect model input shape")
        with self.lock:
            self.interpreter.set_tensor(self.input["index"], values)
            self.interpreter.invoke()
            return self.interpreter.get_tensor(self.output["index"]).copy()
