
import os
import luigi
import numpy as np
import pickle
from astropy.table import Table
from astra.tasks.base import BaseTask
from astra.utils import log
from .base import TheCannonTask, read_training_set

import astra_thecannon as tc


class TrainingSetTarget(BaseTask):

    training_set_path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.training_set_path)


class Train(TheCannonTask):

    threads = luigi.IntParameter(default=1, significant=False)

    default_inverse_variance = luigi.FloatParameter(default=1e6, significant=False)
    
    def requires(self):
        return TrainingSetTarget(training_set_path=self.training_set_path)


    def run(self):

        # Load training set labels and spectra.
        labels, dispersion, training_set_flux, training_set_ivar \
            = read_training_set(self.input().path, self.default_inverse_variance)

        # Set the vectorizer.
        # We sort the label names so that luigi doesn't re-train models if we alter the order.
        vectorizer = tc.vectorizer.PolynomialVectorizer(
            sorted(self.label_names),
            self.order
        )

        # Initiate model.
        model = tc.model.CannonModel(
            labels,
            training_set_flux,
            training_set_ivar,
            vectorizer=vectorizer,
            dispersion=dispersion,
            regularization=self.regularization
            )
    
        log.info(f"Training The Cannon model {model}")
        model.train(threads=self.threads)

        output_path = self.output().path
        log.info(f"Writing The Cannon model {model} to disk {output_path}")
        model.write(output_path)    

    def output(self):
        # By default place the outputs in the same directory as the training set path.
        output_path_prefix, ext = os.path.splitext(self.training_set_path)
        return luigi.LocalTarget(f"{output_path_prefix}-{self.task_id}.pkl")