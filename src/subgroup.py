import pandas as pd
from src.group import Group

class SubGroup(Group):
    def __init__(self, multable: pd.DataFrame, neutral: str):
        """
        Sub group inicializer.

        We identify H < G with the following collection:
            H := (id, multable, Group)
        """
        super.__init__(multable, neutral)

    def Factor(self):
        pass
