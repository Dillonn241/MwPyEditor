import math
import struct


class MwRecord:
    diff_list = ['deleted', 'persists', 'blocked']

    def __init__(self):
        self.subrecords = {}
        self.ordered_subrecords = []
        self.file_name = ''
        self.marked_deleted = False
        self.persists = False
        self.initially_disabled = False
        self.blocked = False
        self.deleted = False

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
        if self.get_record_type() == 'CELL':
            self.deleted = False
            for subrecord in self.ordered_subrecords:
                if subrecord == 'DELE':
                    self.deleted = True
                    break
                elif subrecord == 'FRMR':
                    break
        else:
            self.deleted = 'DELE' in self.subrecords

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
        if self.deleted:
            self.add_int(0, 'DELE')

    def add_subrecord(self, subtype, subdata=b''):
        subrecord = Subrecord(subtype, subdata)
        if subtype not in self.subrecords:
            self.subrecords[subtype] = []
        self.subrecords[subtype].append(subrecord)
        self.ordered_subrecords.append(subrecord)
        return subrecord

    def get_subrecord(self, subtype, index=0):
        subarray = self.subrecords.get(subtype, None)
        if subarray and 0 <= index < len(subarray):
            return subarray[index]

    def get_subrecord_data(self, subtype, index=0, start=0, length=None):
        subarray = self.subrecords.get(subtype, None)
        if subarray and 0 <= index < len(subarray):
            subrecord = subarray[index]
            return subrecord.get_data(start=start, length=length)

    def parse_int(self, subtype, index=0, start=0, length=4):
        subarray = self.subrecords.get(subtype, None)
        if subarray and 0 <= index < len(subarray):
            subrecord = subarray[index]
            return subrecord.parse_int(start=start, length=length)

    def parse_int_array(self, subtype):
        subarray = self.subrecords.get(subtype, None)
        if subarray:
            return [x.parse_int() for x in subarray]

    def parse_uint(self, subtype, index=0, start=0, length=4):
        subarray = self.subrecords.get(subtype, None)
        if subarray and 0 <= index < len(subarray):
            subrecord = subarray[index]
            return subrecord.parse_uint(start=start, length=length)

    def parse_uint_array(self, subtype):
        subarray = self.subrecords.get(subtype, None)
        if subarray:
            return [x.parse_uint() for x in subarray]

    def parse_float(self, subtype, index=0, start=0):
        subarray = self.subrecords.get(subtype, None)
        if subarray and 0 <= index < len(subarray):
            subrecord = subarray[index]
            return subrecord.parse_float(start=start)

    def parse_float_array(self, subtype):
        subarray = self.subrecords.get(subtype, None)
        if subarray:
            return [x.parse_float() for x in subarray]

    def parse_string(self, subtype, index=0, start=0, length=None):
        subarray = self.subrecords.get(subtype, None)
        if subarray and 0 <= index < len(subarray):
            subrecord = subarray[index]
            return subrecord.parse_string(start=start, length=length)

    def parse_string_array(self, subtype):
        subarray = self.subrecords.get(subtype, None)
        if subarray:
            return [x.parse_string() for x in subarray]

    def add_int(self, value, subtype, length=4):
        if value is not None:
            self.add_subrecord(subtype).add_int(value, length=length)

    def add_uint(self, value, subtype, length=4):
        if value is not None:
            self.add_subrecord(subtype).add_uint(value, length=length)

    def add_float(self, value, subtype):
        if value is not None:
            self.add_subrecord(subtype).add_float(value)

    def add_string(self, value, subtype, length=None, terminator=True):
        if value is not None:
            self.add_subrecord(subtype).add_string(value, length=length, terminator=terminator)

    def num_subrecords(self, subtype):
        return len(self.subrecords.get(subtype, []))

    def format_record_details(self, record_detail_list):
        record_detail_list.extend([
            ("\n|Deleted|", 'deleted', False),
            ("\n|Persists|", 'persists', False),
            ("\n|Blocked|", 'blocked', False)
        ])
        string = []
        for record_detail in record_detail_list:
            if hasattr(self, record_detail[1]):
                value = getattr(self, record_detail[1])
                if callable(value):
                    value = value()
                default = record_detail[2] if len(record_detail) > 2 else None
                if value != default:
                    if '{' in record_detail[0]:
                        string.append(record_detail[0].format(value))
                    else:
                        string.append(f"{record_detail[0]}    {value}")
        return ''.join(string)

    def get_id(self):
        return getattr(self, 'id_', str(self))

    def diff(self, other, attr_names=None):
        def diff_attr():
            has_attr_self = hasattr(self, attr_name)
            has_attr_other = hasattr(other, attr_name)
            if has_attr_self:
                attr_self = getattr(self, attr_name)
                if callable(attr_self):
                    attr_self = attr_self()
                if has_attr_other:
                    attr_other = getattr(other, attr_name)
                    if callable(attr_other):
                        attr_other = attr_other()
                    if attr_self != attr_other:
                        string.append(f"\n\t{attr_name}: {attr_self}\n\t{attr_name}: {attr_other}")
                else:
                    string.append(f"\n\tRemoved {attr_name}: {attr_self}")
            elif has_attr_other:
                attr_other = getattr(other, attr_name)
                if callable(attr_other):
                    attr_other = attr_other()
                string.append(f"\n\tAdded {attr_name}: {attr_other}")

        string = []
        for attr_name in MwRecord.diff_list:
            diff_attr()
        if attr_names:
            for attr_name in attr_names:
                diff_attr()
        if string:
            return f"Changed {self}{''.join(string)}"


class Subrecord:
    def __init__(self, subtype, subdata):
        self.record_type = subtype
        self.data = subdata

    def get_data(self, start=0, length=None):
        return self.data[start:start + length] if length else self.data[start:]

    def parse_int(self, start=0, length=4):
        subdata = self.data[start:start + length]
        return int.from_bytes(subdata, byteorder='little', signed=True)

    def parse_uint(self, start=0, length=4):
        subdata = self.data[start:start + length]
        return int.from_bytes(subdata, byteorder='little', signed=False)

    def parse_float(self, start=0):
        subdata = self.data[start:start + 4]
        f = struct.unpack('<f', subdata)[0]
        return 0.0 if math.isnan(f) else f

    def parse_string(self, start=0, length=None):
        subdata = self.get_data(start=start, length=length)
        if 0x00 in subdata:  # zstring
            subdata = subdata[:subdata.index(0x00)]
        format_str = f"{len(subdata)}s"
        return struct.unpack(format_str, subdata)[0].decode('mbcs')

    def add_int(self, value, length=4):
        if value is not None:
            self.data += int.to_bytes(value, byteorder='little', length=length, signed=True)

    def add_uint(self, value, length=4):
        if value is not None:
            self.data += int.to_bytes(value, byteorder='little', length=length, signed=False)

    def add_float(self, value):
        if value is not None:
            self.data += struct.pack('<f', value)

    def add_string(self, value, length=None, terminator=True):
        if value is not None:
            if length:
                if length < len(value):
                 value = value[:length]
                elif length > len(value):
                    value = f"{value:\x00<{length}}"
            format_str = f"{len(value)}s"
            subdata = struct.pack(format_str, value.encode('mbcs'))
            if terminator and not length:
                subdata += struct.pack('b', 0x00)
            self.data += subdata

    def __repr__(self):
        return f"{self.record_type}: {self.data}"
