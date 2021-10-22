from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwTES3(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.version = 1.3
        self.plugin_type = 0
        self.author = ''
        self.description = ''
        self.num_records = 0
        self.masters = {}

    def load(self):
        self.version = self.parse_float('HEDR')
        self.plugin_type = self.parse_uint('HEDR', start=4)
        self.author = self.parse_string('HEDR', start=8, length=32)
        self.description = self.parse_string('HEDR', start=40, length=256)
        self.num_records = self.parse_uint('HEDR', start=296)

        self.masters = {self.parse_string('MAST', index=i):
                        self.parse_uint('DATA', index=i, length=8)
                        for i in range(self.num_subrecords('MAST'))}

    def save(self):
        self.clear_subrecords()
        sub_hedr = self.add_subrecord('HEDR')
        sub_hedr.add_float(self.version)
        sub_hedr.add_uint(self.plugin_type)
        sub_hedr.add_string(self.author, length=32, terminator=False)
        sub_hedr.add_string(self.description, length=256, terminator=False)
        sub_hedr.add_uint(self.num_records)
        for master_name in self.masters:
            self.add_string(master_name, 'MAST')
            self.add_uint(self.masters[master_name], 'DATA', length=8)
        self.save_deleted()

    def requires_expansions(self):
        return self.version == 1.3

    def get_plugin_type(self):
        if self.plugin_type == mwglobals.PluginType.ESP:
            return mwglobals.PluginType.ESP.name
        if self.plugin_type == mwglobals.PluginType.ESM:
            return mwglobals.PluginType.ESM.name
        if self.plugin_type == mwglobals.PluginType.ESS:
            return mwglobals.PluginType.ESS.name

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Version|    {:.2f}", 'version'),
            ("\n|Plugin Type|", 'get_plugin_type'),
            ("\n|Author|", 'author'),
            ("\n|Description|", 'description'),
            ("\n|Num Records|", 'num_records'),
            ("\n|Masters|", 'masters', [])
        ])

    def __str__(self):
        return self.file_name

    def get_id(self):
        return f"{self.file_name} ({self.num_records})"

    def diff(self, other):
        return MwRecord.diff(self, other, ['version', 'plugin_type', 'author', 'description', 'num_records', 'masters'])
