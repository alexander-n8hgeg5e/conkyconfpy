

class ConfigPartBase():
    """
    A part of the config.
    Baseclass to inherit from.
    Can generate its config code.
    """
    @abstractmethod
    def gen_code(self):
        """
        Returns the code.
        """

class KeyValuePair(ConfigPartBase):
    """
    key value pair seperated by seperator.
    """
    def __init__(self,key,sep,val):
        self.key=key
        self.sep=sep
        self.val=val

class Section(ConfigPartBase):
    """
    A section like conky.config or conky.text.
    """
