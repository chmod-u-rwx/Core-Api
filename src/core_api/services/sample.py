
# all business logic here

from uuid import uuid4
from ..models.sample import SampleModel


class SampleServie():

    @staticmethod
    def get_sample_model():
        return SampleModel(id=uuid4(), name="Cotton")