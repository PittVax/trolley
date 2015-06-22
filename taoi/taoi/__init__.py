""" Taoi classes that wrap TreeAge Java objects

Implements a base class, specialized execeptions, and sprecialized variable and
table wrappers.
"""

# common java classes should already be in the classpath, so go ahead and
# import them
import java.rmi.RemoteException
import java.net.ConnectException
import java.rmi.ConnectException
import java.util.Collections as JavaCollections
import java.util.HashMap as JavaHashMap
import java.util.Map as JavaMap

try:
    import utils.set_classpath
    # import the treeage pro object interface
    import com.treeage.treeagepro.oi as TA
except Exception as e:
    raise

import logging
try:
    __main__

except NameError as e:
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger(__name__)

from utils.utility_functions import cat, csv_key_value_dict

###############################################################################
#################################################################### TaoiErrors

class TaoiError(Exception):
    pass
class TaoiVariableError(TaoiError):
    pass
class TaoiTableError(TaoiError):
    pass

###############################################################################
#################################################################### TaoiObject

class TaoiObject(object):
    """ Base class for wrapper TreeAge object (variable or table) """
    def properties(self):
        return [k for k,v in self.__class__.__dict__.items() \
                if type(v) is property]
    def __call__(self):
        """ Overload function operator to return the wrapped TA object """
        return self.tao
    # comment
    @property
    def comment(self):
        return self.tao.getComment()
    @comment.setter
    def comment(self, v):
        self.tao.setComment(v)
    # description
    @property
    def description(self):
        return self.tao.getDescription()
    @description.setter
    def description(self, v):
        self.tao.setDescription(v)
    # name
    @property
    def name(self):
        return self.tao.getName()
    @name.setter
    def name(self, v):
        self.tao.setName(v)

    def update_from_dict(self, dictionary):
        props = self.properties()
        for k,v in dictionary.iteritems():
            if k in props:
                try:
                    msg = 'setting [ %s ] to [ %s ]' % (k, v)
                    v_old = self.__getattribute__(k)
                    msg += ' (originally was [ %s ])' % v_old
                    self.__setattr__(k, v)
                    log.debug('Success ' + msg)
                except Exception as e:
                    log.debug('Failure ' + msg)
                    raise

    def __unicode__(self):
        return '%s %s' % (self.name, self.description)

    def __str__(self):
        return unicode(self).encode('utf-8')

###############################################################################
##################################################################### TaoiTable

class TaoiTable(TaoiObject):
    """ Thin wrapper over a TreeAge Table """
    def __init__(self, table=None, **kwargs):
        try:
            if table is None:
                log.debug(cat('No instance table to copy - instantiating ',
                    'a new one'))
                self.tao = TA.Table()
            elif type(table) == TA.Table:
                log.debug('Copying from supplied table')
                self.tao = table
            elif type(table) == TaoiTable:
                msg = cat('Copy-from-instance logic has not been implemented',
                        ' yet.  Please use an instance of TA.Table')
                log.error(msg)
                raise Exception(msg)
            else:
                msg = '"table" argument of type %s not allowed!' % (
                        type(table),)
                log.error(msg)
                raise Exception(msg)
            self.update_from_dict(kwargs)
        except Exception as e:
            if not isinstance(e, TaoiTableError):
                raise
        self._convert_internal_table()

    def _convert_internal_table(self):
        table = self.tao
        self._rows = []
        for r in table.getRows():
            self._rows.append(r.getValues())
        print(self._rows)



###############################################################################
################################################################## TaoiVariable

class TaoiVariable(TaoiObject):
    """ Thin wrapper over TreeAge Variable """
    def __init__(self, variable=None, **kwargs):
        try:
            if variable is None:
                log.debug(cat('No instance variable to copy - instantiating ',
                    'a new one'))
                self.tao = TA.Variable()
            elif type(variable) == TA.Variable:
                log.debug('Copying from supplied variable')
                self.tao = variable
            elif type(variable) == TaoiVariable:
                msg = cat('Copy-from-instance logic has not been implemented',
                        ' yet.  Please use an instance of TA.Variable')
                log.error(msg)
                raise Exception(msg)
            else:
                msg = '"variable" argument of type %s not allowed!' % (
                        type(variable),)
                log.error(msg)
                raise Exception(msg)
            self.update_from_dict(kwargs)
        except Exception as e:
            if not isinstance(e, TaoiVariableError):
                raise
                
    # variable high value
    @property
    def high(self):
        return self.tao.getHighValue()
    @high.setter
    def high(self, v):
        self.tao.setHighValue(v)
    # variable low value
    @property
    def low(self):
        return self.tao.getLowValue()
    @low.setter
    def low(self, v):
        self.tao.setLowValue()

    # root definition getters/setters
    @property
    def root_set(self):
        return self.tao.isRootDefinitionSet()
    @property
    def root_definition(self):
        if self.root_set:
            return self.tao.getRootDefinition()
        else:
            msg = cat('Root definition does not exist! Check the property ',
                    'TaoiVariable.root_set first!')
            log.error(msg)
            raise TaoiVariableError(msg)
    @root_definition.setter
    def root_definition(self, v):
        if isinstance(v, TA.VariableDefinition):
            self.tao.setRootDefinition(v)
        else:
            msg = cat('root_definition must be set to an instance of %s, ',
                    'but an instance of %s was supplied') % (
                    type(TA.VariableDefinition), type(v))
            log.error(msg)
            raise TaoiVariableError(msg)
    @property
    def root_value(self):
        return self.root_definition.getValue()
    @root_value.setter
    def root_value(self, v):
        self.root_definition.setValue(v)


