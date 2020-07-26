from abc import abstractmethod
from os import linesep
from re import sub
from types import FunctionType as function,MethodType as method
from pprint import pprint
import sys
sys.path.insert(0,"/var/src/pylib")
from pylib.du import dddd,ddd,dd,d0,d1

def indent(txt,width):
    return sub("^"," "*width,txt)

class ConkyConfBase():
    @abstractmethod
    def get_code():
        return code
    
class ConfigElement(ConkyConfBase):
    """
    """
    def __init__(self,z):
        self.value = z
    def get_code(self):
        if issubclass(type(self.value),ConkyConfBase):
            return self.value.get_code()
        else:
            return str(self.value)

class ConfigContainer(ConkyConfBase,list):
    def get_code(self):
        """
        Returns the code.
        """
        code=''
        for thing in self:
            #print(type(thing),thing)
            if issubclass(type(thing),ConkyConfBase):
                #print('thing "{}" issubclass of ConkyConfBase'.format(thing))
                addcode=thing.get_code()
                #print("addcode={}".format(addcode))
                code+=addcode
            else:
                if not type(thing) in (str,int,float):
                    print('thing of type "{}" in {} is not subclass of ConkyConfBase'.format(type(thing),type(self)))
                    print("type={} thing={}".format(type(thing),thing))
                    raise Exception()
                code+=str(thing)
        return code

class ConfigValue(ConfigElement):
    """
    A value like "a",5,true
    """
    def __init__(self,val):
        self.val=val
    def __new__(cls,val):
        if issubclass(type(val),ConkyConfBase):
            # already done
            return val
        elif cls is ConfigValue:
            # make a specialiced subclass
            # if one fits the type
            if type(val) is str:
                return Str(val)
            elif type(val) is int:
                return Int(val)
            elif type(val) is float:
                return Float(val)
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

class Int(int,ConfigValue):
    def get_code(self):
        return repr(self)

class Float(float,ConfigValue):
    def get_code(self):
        return repr(self)

class Str(str,ConfigValue):
    """
    prints a string value the way (quoted)
    needed for the conky config
    """
    def get_code(self):
        return repr(self)

class KeyValuePair(ConfigElement):
    """
    key value pair seperated by seperator.
    """
    def __init__(self,key,sep,val):
        self.key=ConfigElement(key)
        self.sep=ConfigElement(sep)
        self.val=ConfigValue(val)
    def get_code(self):
        key=self.key.get_code()
        sep=self.sep.get_code()
        val=self.val.get_code()
        return "{} {} {}".format(key,sep,val)

class ConfigItem(KeyValuePair):
    def __init__(self,key,val):
        super().__init__(key,"=",val)

class Section(ConfigContainer):
    """
    A section like "conky.config" or "conky.text".
    """
    def __init__(self,head,sep,itemsep,tail,*elements,indent_width=4,indent_tail=True):
        super().__init__((head,))
        self.append(sep)
        indent=" "*indent_width
        if len(elements) > 1:
            for element in elements[:-1]:
                self.append(indent)
                self.append(element)
                self.append(itemsep)
        self.append(indent)
        self.append(elements[-1])
        self.append(sep)
        if indent_tail:
            self.append(indent)
        self.append(tail)

class ConfigSection(Section):
    def __init__(self,*elements,indent_tail=True):
        head=ConfigElement("conky.config = {")
        sep=linesep
        itemsep=","+linesep
        tail="}"+linesep
        super().__init__(head,sep,itemsep,tail,*elements,indent_width=4,indent_tail=indent_tail)

class TextSection(Section):
    def __init__(self,*elements):
        head=ConfigElement("conky.text = [[")
        sep=linesep
        itemsep=""
        tail="]]"+linesep
        super().__init__(head,sep,itemsep,tail,*elements,indent_width=0,indent_tail=False)

class ConkyVariable(ConfigContainer):
    def __init__(self,*z,**zz):
        if len(zz) > 0:
            k=[ k for k in zz.keys()][0]
            v=zz[k]
            key = k
            tv = type(v)
            if not issubclass(tv,ConfigContainer) and not tv in [list,tuple]:
                v=[v]
            parameters = v
        else:
            key        = z[0]
            parameters = z[1:]
        super().__init__()
        self.append("${"+key)
        for p in parameters:
            self.append(" ")
            self.append(p)
        self.append("}")

class Line(ConfigContainer):
    def __init__(self,*elements,**zz):
        super().__init__(elements,**zz)

class Lines(ConfigContainer):
    def __init__(self,*elements):
        super().__init__()
        for e in elements[:-1]:
            self.append(e)
            self.append("\n")
        self.append(elements[-1])

class Style(ConfigContainer):
    def __init__    (
                    self,style_name,style_class,
                    style_value, style_value_arg_address,
                    *elements,vz=[],vzz={},**zz
                    ):
        """
        style_value_arg_address:= if string -> kwarg , if int -> arg pos
        """
        self.style_name = style_name
        self._style_class = style_class
        self._vz=vz
        self._vzz=vzz
        self._style_value=style_value
        self._style_value_arg_address=style_value_arg_address
        self.append(self._gen_head_tail(style_value))
        global style
        if not style_name in style.keys():
            style.update({style_name:style_value})
        super().__init__(elements,**zz)
        self.append(self._gen_head_tail(style_value))

class ColorStyle(Style):
    def __init__(self,value,*z,**zz):
        style_name="color"
        style_class=ConkyVariable
        vz=["color",value]
        style_value_arg_address=1
        vzz={}
        super().__init__(style_name,style_class,value,style_value_arg_address,*z,vz=vz,vzz=vzz,**zz)

class FontStyle(Style):
    def __init__(self,value,*z,**zz):
        style_name="font"
        style_class=ConkyVariable
        vz=["font",value]
        style_value_arg_address=1
        vzz={}
        super().__init__(style_name,style_class,value,style_value_arg_address,*z,vz=vz,vzz=vzz,**zz)

class Font(Section):
    def __init__(self,name,size,*z,**options):
        k=ConfigElement
        self.size=size
        parts = [k(name),Line(k('size'),k("="),k(size)),
                *[k(v) for v in z],
                *[Line(k(v),k("="),k(vv)) for v,vv in options.items()]
                ]
        empty=k("")
        super().__init__(k("${font "), empty,k(":"), k("}"),*parts,indent_width=0)
    def get_code(self):
        return super().get_code()

class Color(ConfigElement):
    def __init__(self,int_value):
        self.value=int_value
    def get_code(self):
        fs='${{color #{:06x}}}'
        return fs.format(self.value)

class VOffset(ConkyVariable):
    def __init__(self,val):
        super().__init__(voffset=val)

class HOffset(ConkyVariable):
    def __init__(self,val,*z,**zz):
        super().__init__(offset=val)

class RightOf(Lines):
    def __init__(self,x,y,*elements,**zz):
        lines=[]
        if len(elements) > 0:
            e0=elements[0]
            lines.append(Line("\n",VOffset(y),HOffset(x),*e0))
            if len(elements) > 1:
                ee = elements[1:]
                for e in ee:
                    lines.append(Line( HOffset(x) , *e ))
        super().__init__(*lines,**zz)

class ConditionalOperator(str,ConfigElement):
    def __init__(self,z):
        if not self.valid():
            raise Exception('ERROR: Operator "{}" is not valid.'.format(self.get_code()))
        super().__init__(z)

    def get_code(self):
        return str(self)
    def valid(self):
        return self.get_code() in ['>', '<', '>=', '<=', '==', '!=']

class ConditionalExp(ConfigContainer):
    """
    Takes 2 exps, 2 results, one op and gives ConfigPartBase object.
    conky syntax:
    =============
    {if_match exp0 op exp1}result_true${else}result_false${endif} 
    """
    def __init__(self,exp0,op_string,exp1,result_true,result_false,indent_width=0):
        self.op = ConditionalOperator(op_string)
        self.result_true  = result_true
        self.result_false = result_false
        self.exp0         = Line(exp0)
        self.exp1         = Line(exp1)
    def get_code(self):
        fs = "${{if_match {} {} {}}}{}${{else}}{}${{endif}}"
        anames  = [ 'exp0', 'op', 'exp1', 'result_true', 'result_false' ]
        attrs   = [ getattr(self,a) for a in anames ]
        codes   = [ o.get_code() for o in attrs ]
        #for o in attrs:
        #    if type(o.get_code()) is str:
        #        print(o.get_code(),type(o))
        return fs.format(*codes)

class ConditionalColor(ConditionalExp):
    def __init__(self,exp0,op_string,exp1,color_true,colored_result_true,color_false,colored_result_false,**zz):
        res_true  = L(Color(color_true),colored_result_true)
        res_false = L(Color(color_false),colored_result_false)
        super().__init__(exp0,op_string,exp1,res_true,res_false,**zz)

# global style variable
style = {}
font_size=None

# ABBREVIATIONS
# =============
# all uppercase accepts multiple ConfigPartBase objects   ([O]{2,})
# all lowercase one or more non ConfigPartBase objects    ([o]{1,})
# upper and lower mixed means mixed types, or no at all  ([oO]{0,})

L  = Line
LL = Lines
C  = ColorStyle
c  = Color
v  = ConkyVariable
F  = FontStyle
f  = Font
vo = VOffset
ho = HOffset
s  = Str        # use for things that must be escaped
RO = RightOf
Ce = ConditionalExp
co = ConditionalOperator
Cc = ConditionalColor
k  = ConfigElement

        
# vim: set foldlevel=0 foldmethod=indent foldnestmax=1 :
