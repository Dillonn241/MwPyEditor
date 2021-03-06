import mwglobals
from mwrecord import MwRecord


class MwTES3(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.version = self.get_subrecord_float("HEDR", start=0, length=4)
        self.plugin_type = self.get_subrecord_int("HEDR", start=4, length=4)
        self.author = self.get_subrecord_string("HEDR", start=8, length=32)
        self.description = self.get_subrecord_string("HEDR", start=40, length=256)
        self.num_records = self.get_subrecord_int("HEDR", start=296, length=4)
        
        self.masters = {}
        for i in range(self.num_subrecords("MAST")):
            master_name = self.get_subrecord_string("MAST", index=i)
            master_size = self.get_subrecord_int("DATA", index=i)
            self.masters[master_name] = master_size
    
    """def save(self):
        self.set_subrecord_float(self.version, "HEDR", start=0, length=4)
        self.set_subrecord_int(self.plugin_type, "HEDR", start=4, length=4)
        self.set_subrecord_string(self.author, "HEDR", start=8, length=32)
        self.set_subrecord_string(self.description, "HEDR", start=40, length=256)
        self.num_records = len([x for x in mwglobals.ordered_records if x.file_name == self.file_name]) - 1
        self.set_subrecord_int(self.num_records, "HEDR", start=296, length=4)"""
    
    def requires_expansions(self):
        if self.version == 1.3:
            return True
        return False

    def get_plugin_type(self):
        if self.plugin_type == mwglobals.PluginType.ESP:
            return "ESP"
        if self.plugin_type == mwglobals.PluginType.ESM:
            return "ESM"
        if self.plugin_type == mwglobals.PluginType.ESS:
            return "ESS"
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Version|    {:.2f}", "version"),
            ("\n|Plugin Type|", "get_plugin_type"),
            ("\n|Author|", "author"),
            ("\n|Description|", "description"),
            ("\n|Num Records|", "num_records"),
            ("\n|Masters|", "masters", [])
        ])
    
    def __str__(self):
        return self.description
    
    def get_id(self):
        return "TES3"
    
    def diff(self, other):
        MwRecord.diff(self, other, ["version", "plugin_type", "author", "description", "num_records", "masters"])
