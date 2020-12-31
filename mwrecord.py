import struct
import math
from mwglobals import *

class MwRecord:
    def __init__(self):
        self.subrecords = {}
        self.ordered_subrecords = []
    
    def get_record_type(self):
        return self.__class__.__name__[2:]
    
    def load_universal(self, flags):
        self.deleted = "DELE" in self.subrecords
        self.marked_deleted = (flags & 0x20) == 0x20
        self.persists = (flags & 0x400) == 0x400
        self.initially_disabled = (flags & 0x800) == 0x800
        self.blocked = (flags & 0x2000) == 0x2000
    
    def save_universal(self):
        if self.deleted:
            pass
        flags = 0x0
        if self.marked_deleted:
            flags |= 0x20
        if self.persists:
            flags |= 0x400
        if self.initially_disabled:
            flags |= 0x800
        if self.blocked:
            flags |= 0x2000
        return flags
    
    def add_subrecord(self, subtype, subdata):
        if subtype not in self.subrecords:
            self.subrecords[subtype] = []
        subrecord = Subrecord()
        subrecord.record_type = subtype
        subrecord.data = subdata
        self.subrecords[subtype] += [subrecord]
        self.ordered_subrecords += [subrecord]
    
    def get_subrecord(self, subtype, index=0):
        subarray = self.subrecords.get(subtype, None)
        if subarray != None:
            return subarray[index]
    
    def get_subrecord_int(self, subtype, index=0, start=None, length=None, signed=True):
        subarray = self.subrecords.get(subtype, None)
        if subarray != None:
            subrecord = subarray[index]
            return subrecord.get_int(start=start, length=length, signed=signed)
    
    def get_subrecord_float(self, subtype, index=0, start=None, length=None):
        subarray = self.subrecords.get(subtype, None)
        if subarray != None:
            subrecord = subarray[index]
            return subrecord.get_float(start=start, length=length)
    
    def get_subrecord_string(self, subtype, index=0, start=None, length=None):
        subarray = self.subrecords.get(subtype, None)
        if subarray != None:
            subrecord = subarray[index]
            return subrecord.get_string(start=start, length=length)
    
    def set_subrecord_int(self, value, subtype, index=0, start=None, length=None, signed=True):
        self.subrecords[subtype][index].set_int(value, start=start, length=length, signed=signed)
    
    def set_subrecord_float(self, value, subtype, index=0, start=None, length=None):
        self.subrecords[subtype][index].set_float(value, start=start, length=length)
    
    def set_subrecord_string(self, value, subtype, index=0, start=None, length=None):
        self.subrecords[subtype][index].set_string(value, start=start, length=length)
    
    def num_subrecords(self, subtype):
        subarray = self.subrecords.get(subtype, None)
        if subarray != None:
            return len(subarray)
        return 0
    
    def format_record_details(self, record_detail_list):
        record_detail_list += [
        ("\n|Deleted|", "deleted", False),
        ("\n|Persists|", "persists", False),
        ("\n|Blocked|", "blocked", False),
        ]
        string = []
        for record_detail in record_detail_list:
            display = record_detail[0]
            if "{" not in record_detail[0]:
                display += "    {}"
            if hasattr(self, record_detail[1]):
                value = getattr(self, record_detail[1])
                if callable(value):
                    value = value()
            else:
                value = record_detail[1]
            if len(record_detail) > 2:
                if value != record_detail[2]:
                    string.append(display.format(value))
            elif value:
                string.append(display.format(value))
        return "".join(string)
    
    def get_id(self):
        return self.id
    
    def diff(self, other, attrs=[]):
        all_attrs = attrs + ["deleted", "persists", "blocked"]
        string = []
        for attr in all_attrs:
            has_attr_self = hasattr(self, attr)
            has_attr_other = hasattr(other, attr)
            if has_attr_self:
                if has_attr_other:
                    get_attr_self = str(getattr(self, attr))
                    get_attr_other = str(getattr(other, attr))
                    if get_attr_self != get_attr_other:
                        string.append("\n\t{0}: {1}\n\t{0}: {2}".format(attr, get_attr_self, get_attr_other))
                else:
                    string.append("\n\tRemoved {}: {}".format(attr, getattr(self, attr)))
            elif has_attr_other:
                string.append("\n\tAdded {}: {}".format(attr, getattr(other, attr)))
        if string:
            print("Changed", str(self) + "".join(string))

class Subrecord:
    def get_data(self, start=None, length=None):
        if start != None:
            if length != None:
                return self.data[start:start + length]
            else:
                return self.data[start:]
        elif length != None:
            return self.data[:length]
        return self.data
    
    def get_int(self, start=None, length=None, signed=True):
        subdata = self.get_data(start=start, length=length)
        return int.from_bytes(subdata, byteorder="little", signed=signed)
    
    def get_float(self, start=None, length=None):
        subdata = self.get_data(start=start, length=length)
        f = struct.unpack("<f", subdata)[0]
        if math.isnan(f):
            return 0.0
        return f
    
    def get_string(self, start=None, length=None):
        if start is None and length is None and 0x00 in self.data: # zstring
            subdata = self.data[:self.data.index(0x00)]
        else:
            subdata = self.get_data(start=start, length=length)
            if 0x00 in subdata:
                subdata = subdata[:subdata.index(0x00)]
        format_str = str(len(subdata)) + "s"
        return struct.unpack(format_str, subdata)[0].decode("mbcs")
    
    def set_data(self, subdata, start=None, length=None):
        if start != None:
            if length != None:
                self.data = self.data[:start] + subdata + self.data[start + length:]
            else:
                self.data = self.data[:start] + subdata
        elif length != None:
            self.data = subdata + self.data[length:]
        else:
            self.data = subdata
    
    def set_int(self, value, start=None, length=None, signed=True):
        subdata = int.to_bytes(value, byteorder="little", signed=signed, length=length)
        self.set_data(subdata, start=start, length=length)
    
    def set_float(self, value, start=None, length=None):
        subdata = struct.pack("<f", value)
        self.set_data(subdata, start=start, length=length)
    
    def set_string(self, value, start=None, length=None):
        format_str = (str(length) if length != None else str(len(value))) + "s"
        subdata = struct.pack(format_str, value.encode("mbcs"))
        if start is None and length is None:
            subdata += struct.pack("b", 0x00)
        self.set_data(subdata, start=start, length=length)