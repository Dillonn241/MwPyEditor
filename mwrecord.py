import math
import struct

class MwRecord:
    def __init__(self):
        self.clear_subrecords()
    
    def clear_subrecords(self):
        self.subrecords = {}
        self.ordered_subrecords = []
    
    def get_record_type(self):
        return self.__class__.__name__[2:]
    
    def load_flags(self, flags):
        self.marked_deleted = (flags & 0x20) == 0x20
        self.persists = (flags & 0x400) == 0x400
        self.initially_disabled = (flags & 0x800) == 0x800
        self.blocked = (flags & 0x2000) == 0x2000
    
    def load_deleted(self):
        self.deleted = "DELE" in self.subrecords

    def save_flags(self):
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
    
    def save_deleted(self):
            self.add_subrecord_int(0, "DELE")
        subrecord = Subrecord(subtype, subdata)
        if subtype not in self.subrecords:
            self.subrecords[subtype] = []
        self.subrecords[subtype] += [subrecord]
        self.ordered_subrecords += [subrecord]
        return subrecord
    
    def get_subrecord(self, subtype, index=0):
        subarray = self.subrecords.get(subtype, None)
        if subarray != None:
            return subarray[index]
    
    def get_subrecord_data(self, subtype, index=0, start=None, length=None):
        subarray = self.subrecords.get(subtype, None)
        if subarray != None:
            subrecord = subarray[index]
            return subrecord.get_data(start=start, length=length)
    
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
    
    def add_subrecord_int(self, value, subtype, length=4, signed=True):
        if value is not None:
            self.add_subrecord(subtype).add_int(value, length=length, signed=signed)
    
    def add_subrecord_float(self, value, subtype):
        if value is not None:
            self.add_subrecord(subtype).add_float(value)
    
    def add_subrecord_string(self, value, subtype, terminator=True):
        if value is not None:
            self.add_subrecord(subtype).add_string(value, terminator=terminator)
    
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
            if hasattr(self, record_detail[1]):
                value = getattr(self, record_detail[1])
                if callable(value):
                    value = value()
                default = record_detail[2] if len(record_detail) > 2 else None
                if value != default:
                    display = record_detail[0]
                    if "{" not in record_detail[0]:
                        display += "    {}"
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
    def __init__(self, subtype, subdata):
        self.record_type = subtype
        self.data = subdata
    
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
        subdata = self.get_data(start=start, length=length)
        if 0x00 in subdata: # zstring
            subdata = subdata[:subdata.index(0x00)]
        format_str = str(len(subdata)) + "s"
        return struct.unpack(format_str, subdata)[0].decode("mbcs")
    
    def add_int(self, value, length=4, signed=True):
        self.data += int.to_bytes(value, byteorder="little", length=length, signed=signed)
    
    def add_float(self, value):
        self.data += struct.pack("<f", value)
    
    def add_string(self, value, terminator=True):
        format_str = str(len(value)) + "s"
        subdata = struct.pack(format_str, value.encode("mbcs"))
        if terminator:
            subdata += struct.pack("b", 0x00)
        self.data += subdata