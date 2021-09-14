from hashlib import sha256
from datetime import datetime
from opcua import ua, Server, Subscription
from opcua.server.user_manager import UserManager
from opcua.common.type_dictionary_buider import \
    DataTypeDictionaryBuilder, get_ua_class
from inspect import signature, getmembers, ismethod
from typing import List, Tuple
import time

ParamDesc = List[Tuple[str, type]]

class SubHandler(object):
    def __init__(self, updateCallback):
        self._callback = updateCallback

    def datachange_notification(self, node, val, data):
        try:
            if (val != None):
                self._callback(node, val, data.monitored_item.Value)
        except Exception as e:
            print(e)
            pass
        # self.storage.save_node_value(node.nodeid, data.monitored_item.Value)

    def event_notification(self, event):
        # ignore events
        pass


def convertValueFromOPC(value):
    return value.Value

def createNodeID(nsIdx: int, nodePath: str):
    nid = ua.NodeId(nodePath, nsIdx, ua.uatypes.NodeIdType.String)
    return nid

def convertValueToOPC(value): #Gibt tuple
    t = type(value)
    if t is str:
        return [ua.Variant(value, ua.VariantType.String)]
    elif t is float:
        return [ua.Variant(value, ua.VariantType.Double)]
    elif t is int:
        return [ua.Variant(value, ua.VariantType.Int32)]
    elif t is bool:
        return [ua.Variant(value, ua.VariantType.Boolean)]
    else:
        return [ua.Variant(value, ua.VariantType.Variant)]


def getOPCType(t): #Gibt eingegebenen Datentyp als OPCType aus
    if t is str:
        return ua.VariantType.String
    elif t is float:
        return ua.VariantType.Double
    elif t is int:
        return ua.VariantType.Int32
    elif t is bool:
        return ua.VariantType.Boolean
    else:
        return ua.VariantType.Variant


class SimpleUserManager():
    def __init__(self, user: str, pwd: str): #Erstellt ein User mit PW in der Klasse SimpleUserManager
        self.users = {user: pwd}

    def user_manager(self, isession, username: str, password: str):
        print(isession, username, password)
        isession.user = UserManager.User

        a = sha256(password).hexdigest()
        return username in self.users and a == self.users[username]


class valueContainer:
    def __init__(self, value, valueNode, callback = None):
        self.value = value
        self.valueNode = valueNode
        self.callback = callback


class ua_server(object):
    """OPC UA server to publish values"""

    def __init__(self, port: int, route: str, uri: str,
                 user: str = "", pwd: str = ""):
        if(route.startswith("/")):
            route = route[1:]
        if(route.endswith("/")):
            route = route[:-1]

        self._dicValues = dict()
        self._dicEvents = dict()
        self._dicTypes = dict()

        self._server = Server()
        ep = "opc.tcp://0.0.0.0:{0}/{1}/".format(port, route)
        self._server.set_endpoint(ep)
        print(ep)

        # setup our own namespace, not really necessary but should as spec
        self._idx = self._server.register_namespace(uri)

        # add securety and user
        cert = False  # no certificate available
        if cert:

            # use certificate here
            self._server.load_certificate("")
            self._server.load_private_key("")
            a = [ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt]
            self._server.set_security_policy(a)
        else:
            a = [ua.SecurityPolicyType.NoSecurity]
            self._server.set_security_policy(a)

        if user != "":
            x = sha256(pwd.encode('utf-8')).hexdigest()
            self._usermgr = SimpleUserManager(user, x)
            self._server.set_security_IDs(["Username"])

            # set the user_manager function
            u = self._usermgr.user_manager
            self._server.user_manager.set_user_manager(u)

        # get Objects node, this is where we should put our nodes
        self._objects = self._server.get_objects_node()
        self._server.set_server_name("LAI OPC UA Server")
        self._dict_builder = DataTypeDictionaryBuilder(
            self._server, self._idx, uri, 'CustomStructs'
        )
        self._server.start()
        self._sub = self._create_subscription(SubHandler(self._itemUpdated))

    def _create_subscription(self, handler):
        params = ua.CreateSubscriptionParameters()
        params.RequestedPublishingInterval = 10
        params.RequestedLifetimeCount = 3000
        params.RequestedMaxKeepAliveCount = 10000
        params.MaxNotificationsPerPublish = 0
        params.PublishingEnabled = True
        params.Priority = 0
        return Subscription(self._server.iserver.isession, params, handler)

    def _itemUpdated(self,  node, value, opcValue):
        vn = None
        name = ''
        # hier noch effektiver die zugehörigen Node finden
        for key, val in self._dicValues.items():
            if val.valueNode == node:
                vn = val
                name = key
                break
        if (vn != None):
            # internal Update to set correct state and ServerTimestamp when value has changed
            if (value != vn.value):
                if(opcValue.StatusCode == ua.StatusCode(ua.StatusCodes.BadWaitingForInitialData)):
                    opcValue.StatusCode = ua.StatusCode(ua.StatusCodes.Good)

                ts = datetime.utcnow()
                opcValue.ServerTimestamp = ts
                if (opcValue.SourceTimestamp == None):
                    opcValue.SourceTimestamp = ts
                    self._dicValues[key].value = value

                # publish new value
                if(vn.callback != None):
                    vn.callback(name, value)

    def shutdown(self):
        self._server.stop()


    def registerValue(self, itemName: str, initValue, writeable: bool = False, description: str = '', updateCallback = None):
            parts = itemName.split("/")
            valName = parts[-1]
            objNames = parts[:-1]
            node = self._objects
            objDone = list()
            for s in objNames:
                objDone.append(s);
                childs = node.get_children()
                r = filter(lambda o: o.get_browse_name().Name == s, childs)
                r = list(r)
                if len(r) > 0:
                    node = r[0]
                else:
                    nid = createNodeID(self._idx, '/'.join(objDone))
                    node = node.add_folder(nid, s)

            nid = createNodeID(self._idx, itemName)
           
            dv = ua.DataValue(initValue, status = ua.StatusCode(ua.StatusCodes.BadWaitingForInitialData))
            v = node.add_variable(nid, valName, dv)

            v.set_value(dv)
            if(writeable):
                v.set_writable()

            if (description != ''):
                v.set_attribute(
                    ua.AttributeIds.Description,
                    ua.DataValue(ua.LocalizedText(description))
                )
            self._dicValues[itemName] = valueContainer(initValue, v, updateCallback)

            self._sub.subscribe_data_change(v)
            


    def setValue(self, itemName: str, timestamp: datetime, value, sourceTimestamp: datetime = None):
        dv = ua.DataValue(value, status = ua.StatusCode(ua.StatusCodes.Good))
        if sourceTimestamp is None:
            sourceTimestamp = timestamp
        dv.SourceTimestamp = sourceTimestamp
        dv.ServerTimestamp = timestamp
        if not(itemName in self._dicValues):
            self.registerValue(itemName, value)
        v = self._dicValues[itemName]
        if v.value != value:
            v.value = value
            v.valueNode.set_value(dv)

    def registerEvent(self, itemName: str, eventName: str,
                      params: ParamDesc = []):
        objNames = itemName.split("/")
        node = self._objects
        objDone = list()
        for s in objNames:
            objDone.append(s)
            childs = node.get_children()
            r = filter(lambda o: o.get_browse_name().Name == s, childs)
            r = list(r)
            if len(r) > 0:
                node = r[0]
            else:
                nid = createNodeID(self._idx, '/'.join(objDone))
                node = node.add_folder(nid, s)
        if eventName not in self._dicEvents:
            e = self._server.nodes.base_event_type.add_object_type(
                self._idx, eventName
            )
            for param in params:
                e.add_property(
                    self._idx, param[0], ua.Variant(0, getOPCType(param[1]))
                )
            self._dicEvents[eventName] = \
                self._server.get_event_generator(e, node)

    def raiseEvent(self, eventName: str, message: str, params: dict = {}):
        if eventName in self._dicEvents:
            self._dicEvents[eventName].event.Message = \
                ua.LocalizedText(message)
            for key in getmembers(self._dicEvents[eventName].event):
                if key[0] in params:
                    setattr(
                        self._dicEvents[eventName].event,
                        key[0],
                        params[key[0]]
                    )
            self._dicEvents[eventName].trigger()

    def addMethod(self, methodName: str, f, description: str = ''):
        parts = methodName.split("/")
        methName = parts[-1]
        objNames = parts[:-1]
        node = self._objects
        objDone = list()
        for s in objNames:
            objDone.append(s)
            childs = node.get_children()
            r = list(filter(lambda o: o.get_browse_name().Name == s, childs))
            if len(r) > 0:
                node = r[0]
            else:
                nid = createNodeID(self._idx, '/'.join(objDone))
                node = node.add_folder(nid, s)

        sig = signature(f)

        # add index, name, and functionpointer to args
        nid = createNodeID(self._idx, methodName)
        args = [nid, methName, f]

        b = True
        inparams = list()
        for k, v in sig.parameters.items():
            if b:
                # first Parameter is only for internal use
                b = False
            else:
                pt = getOPCType(v.annotation)
                inparams.append(pt)

        # add in paramter to args
        args.append(inparams)

        # add return value to args
        rt = [getOPCType(sig.return_annotation)]
        args.append(rt)

        m = node.add_method(*args)
        if m is None:
            print("Failed to add method")
        else:
            if (description != ''):
                m.set_attribute(
                    ua.AttributeIds.Description,
                    ua.DataValue(ua.LocalizedText(description))
                )

        print("new method({0}) added".format(methodName))

    def registerStruct(self, structClass: type):
        name = str(structClass.__name__)
        # name = 'basic_structure'
        variables = [
            i for i in structClass.__dict__.keys() if not
            i.startswith('__') and not ismethod(i)
        ]
        if name in self._dicTypes:
            raise Exception(f'Struct {name} already registered')
        else:
            struct = self._dict_builder.create_data_type(name)
            for v in variables:
                struct.add_field(v, getOPCType(type(getattr(structClass, v))))
            self._dicTypes[name] = struct
            self._dict_builder.set_dict_byte_string()
            self._server.load_type_definitions()

    def setStruct(self, itemName: str, struct: object):
        name = str(type(struct).__name__)
        if name in self._dicTypes:
            parts = itemName.split("/")
            valName = parts[-1]
            objNames = parts[:-1]
            node = self._objects
            objDone = list()
            for s in objNames:
                objDone.append(s)
                childs = node.get_children()
                r = filter(lambda o: o.get_browse_name().Name == s, childs)
                r = list(r)
                if len(r) > 0:
                    node = r[0]
                else:
                    nid = createNodeID(self._idx, '/'.join(objDone))
                    node = node.add_folder(nid, s)

            nid = createNodeID(self._idx, itemName)
            v = node.add_variable(
                nid, valName, ua.Variant(None, ua.VariantType.Null),
                datatype=self._dicTypes[name].data_type
            )
            msg = get_ua_class(name)()
            variables = [
                i for i in type(struct).__dict__.keys() if not
                i.startswith('__') and not ismethod(i)
            ]
            for key in variables:
                val = getattr(struct, key)
                setattr(msg, key, val)

            v.set_value(msg)

        else:
            raise Exception(f'Struct {name} not found')
