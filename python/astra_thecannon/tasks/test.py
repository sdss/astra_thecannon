
import os
import luigi
import pickle
import numpy as np
from astra.tasks.base import BaseTask
from astra.utils import log
from astra.tools.spectrum import Spectrum1D

import astra_thecannon as tc

from .base import TheCannonTask
from .train import Train

'''
from .train import Train

class DummyTask(BaseTask):
    def output(self):
        raise NotImplementedError(
            "You must overwrite the `requires()` function in the `astra_thecannon.tasks.Test` class "
            "so that it provides an 'observation' and 'model' task."
        )
'''


class Test(TheCannonTask):

    # TODO: Allow for explicit initial values?
    N_initialisations = luigi.IntParameter(default=10)
    use_derivatives = luigi.BoolParameter(default=True)
    
    def requires(self):
        raise NotImplementedError(
            "You must overwrite the `requires()` function in the `astra_thecannon.tasks.Test` class "
            "so that it provides a dictionary with keys 'model' and 'observation', and tasks as values."
        )


    def run(self):

        model = tc.CannonModel.read(self.input()["model"].path)
        observation = Spectrum1D.read(self.input()["observation"].path)

        # Re-sample observations on to the model dispersion.
        o_x = observation.wavelength.value
        o_f = np.atleast_2d(observation.flux.value)
        o_i = np.atleast_2d(observation.uncertainty.quantity.value)

        N, P = shape = (o_f.shape[0], model.dispersion.size)
        flux = np.empty(shape)
        ivar = np.empty(shape)

        for i in range(N):
            flux[i] = np.interp(model.dispersion, o_x, o_f[i])
            ivar[i] = np.interp(model.dispersion, o_x, o_i[i])

        kwds = dict(
            flux=flux,
            ivar=ivar,
            initialisations=self.N_initialisations,
            use_derivatives=self.use_derivatives
        )

        labels, cov, metadata = model.test(**kwds)

        log.info(f"Inferred labels: {labels}")
        log.info(f"Metadata: {metadata}")

        with open(self.output().path, "wb") as fp:
            pickle.dump(
                (labels, cov, metadata), 
                fp
            )


    def output(self):
        # By default place the outputs in the same directory as the observation input path.
        output_path_prefix, ext = os.path.splitext(self.input()["observation"].path)
        return luigi.LocalTarget(f"{output_path_prefix}-{self.task_id}.pkl")


