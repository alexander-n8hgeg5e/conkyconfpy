from abc import abstractmethod
from os import linesep
from re import sub

def indent(txt,width):
    return sub("^"," "*width,txt)

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
        if issubclass(type(val),ConfigPartBase):
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
        # In this case the super probably "Object".
        # In case cls is of this class
        # and no specific subclass was found
        # use default __new__ to make this class.
        if type(val) is bool:
            return super().__new__(cls)
        else:
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
        return repr(self.val).lower()

class Int(ConfigValue,int):
    def get_code(self):
        return repr(self)

class Str(ConfigValue,str):
    """
    prints a string value the way (quoted)
    needed for the conky config
    """
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

class ConfigItem(KeyValuePair):
    def __init__(self,key,val):
        super().__init__(key,"=",val)

class Section(ConfigPartBase,list):
    """
    A section like "conky.config" or "conky.text".
    """
    def __init__(self,head,sep,elements,itemsep,tail,indent_width=4):
        self.head = head
        self.tail = tail
        self.sep  = sep
        self.itemsep = itemsep
        self.indent_width=indent_width
        super().__init__(elements)

    def get_code(self):
        code  = self.head.get_code() + self.sep.get_code()
        for thing in self:
            line  = thing.get_code()
            line += self.itemsep.get_code()
            line  = indent(line,self.indent_width)
            code += line
        code += self.tail.get_code()
        return code

class ConfigSection(Section):
    def __init__(self,*z):
        head = KeyValuePair("conky.config","=",ConfigKey("{"))
        tail = ConfigKey("}")
        sep  = ConfigKey(linesep)
        itemsep  = ConfigKey("," + linesep)
        super().__init__(head,sep,[*z],itemsep,tail)

class TextSection(Section):
    def __init__(self,*z):
        head = KeyValuePair("conky.text","=",ConfigKey("[["))
        tail = ConfigKey("]]")
        sep  = ConfigKey(linesep)
        itemsep  = ConfigKey(linesep)
        super().__init__(head,sep,[*z],itemsep,tail)

class V(ConfigPartBase):
    def __init__(self,*z,**zz):
        if len(zz) > 0:
            k,v = [ (k,v) for k,v in zz.items()][0]
            self.key        = k
            if not hasattr(v,"__iter__"):
                v=[v]
            self.parameters = v
        else:
            self.key        = z[0]
            self.parameters = z[1:]
    def get_code(self):
        parameters = [str(v) for v in self.parameters]
        code="${"+self.key
        if len(parameters)>0:
            code+=" "+" ".join(parameters)
        code+="}"
        return code

class L(Section):
    def __init__(self,*elements,indent_width=0):
        #                head,sep,elements,itemsep,tail,indent_width=4
        empty=ConfigKey("")
        super().__init__(empty,empty,elements,empty,empty,indent_width=indent_width)


        
# vim: set foldlevel=0 foldmethod=indent foldnestmax=1 :
