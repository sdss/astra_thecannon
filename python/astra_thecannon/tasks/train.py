
import os
import luigi
import numpy as np
from astropy.table import Table
from astra.tasks.base import BaseTask
from astra.utils import log
from astra_thecannon.tasks.base import TheCannonMixin, read_training_set

import astra_thecannon as tc



class TrainingSetTarget(BaseTask):

    training_set_path = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.training_set_path)



class TrainTheCannon(TheCannonMixin):

    regularization = luigi.FloatParameter(default=0)
    threads = luigi.IntParameter(default=1, significant=False)
    default_inverse_variance = luigi.FloatParameter(default=1e6, significant=False)
    plot = luigi.BoolParameter(default=True, significant=False)

    def requires(self):
        return TrainingSetTarget(training_set_path=self.training_set_path)


    def run(self):

        # Load training set labels and spectra.
        labels, dispersion, training_set_flux, training_set_ivar = read_training_set(
            self.input().path, 
            self.default_inverse_variance
        )

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

        if self.plot:
            # Plot zeroth and first order coefficients.
            from astra_thecannon import plot
            fig = plot.theta(
                model,
                indices=np.arange(1 + len(model.vectorizer.label_names)),
                normalize=False
            )
            fig.savefig(f"{self.output_prefix}-theta.png")

            # Plot scatter.
            fig = plot.scatter(model)
            fig.savefig(f"{self.output_prefix}-scatter.png")

            # Plot one-to-one.
            test_labels, test_cov, test_meta = model.test(
                training_set_flux, 
                training_set_ivar,
                initial_labels=model.training_set_labels
            )
            fig = plot.one_to_one(model, test_labels, cov=test_cov)
            fig.savefig(f"{self.output_prefix}-one-to-one.png")
            
    

    @property
    def output_prefix(self):
        # By default place the outputs in the same directory as the training set path.
        output_path_prefix, ext = os.path.splitext(self.training_set_path)
        return f"{output_path_prefix}-{self.task_id}"


    def output(self):
        return luigi.LocalTarget(f"{self.output_prefix}.pkl")
        