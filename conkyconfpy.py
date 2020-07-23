from abc import abstractmethod

class ConfigPartBase():
    """
    A part of the config.
    Baseclass to inherit from.
    Can generate its config code.
    """
    @abstractmethod
    def get_code(self):
        """
        Returns the code.
        """

class ConfigValue(ConfigPartBase):
    """
    A value like "a",5,true
    """
    def __init__(self,val):
        self.val=val
    def __new__(cls,val):
        if val.__class__.__subclasscheck__(ConfigValue):
            # already done
            return val
        elif cls is ConfigValue:
            # make a specialiced subclass
            # if one fits the type
            if type(val) is str:
                return Str(val)
            elif type(val) is int:
                return Int(val)
            elif type(val) is bool:
                return Bool(val)
        # The case this method is inherited
        # from one of these classes
        # use default __new__ to make them.
        # In case cls is of this class
        # and no specific subclass was found
        # use default __new__ to make this class.
        return super().__new__(cls,val)
    def get_code(self):
        """
        default get code method for values
        """
        return repr(self)

class Bool(ConfigValue):
    def __init__(self,val):
        self.val=bool(val)
    def __bool__(self):
        return bool(self.val)
    def get_code(self):
        return repr(self).lower()

class Int(ConfigValue,int):
    def get_code(self):
        return repr(self)

class Str(ConfigValue,str):
    def get_code(self):
        return repr(self)

class ConfigKey(ConfigPartBase,str):
    def get_code(self):
        return str(self)

class KeyValuePair(ConfigPartBase):
    """
    key value pair seperated by seperator.
    """
    def __init__(self,key,sep,val):
        self.key=ConfigKey(key)
        self.sep=ConfigKey(sep)
        self.val=ConfigValue(val)
    def get_code(self):
        key=self.key.get_code()
        sep=self.sep.get_code()
        val=self.val.get_code()
        return "{} {} {}".format(key,sep,val)

class Section(ConfigPartBase):
    """
    A section like "conky.config" or "conky.text".
    """
# vim: set foldlevel=0 foldmethod=indent foldnestmax=1 :
