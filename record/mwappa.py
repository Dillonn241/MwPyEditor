import mwglobals
from mwrecord import MwRecord


class MwAPPA(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.type = mwglobals.APPA_TYPES[self.get_subrecord_int("AADT", start=0, length=4)]
        self.quality = self.get_subrecord_float("AADT", start=4, length=4)
        self.weight = self.get_subrecord_float("AADT", start=8, length=4)
        self.value = self.get_subrecord_int("AADT", start=12, length=4)
        self.icon = self.get_subrecord_string("ITEX")
        self.script = self.get_subrecord_string("SCRI")
        mwglobals.object_ids[self.id] = self
    
    def wiki_entry(self):
        return ("|-\n"
                "|[[File:TD3-icon-tool-" + self.icon + ".png]]\n"
                "|'''{{Anchor|" + self.name + "}}'''<br>{{Small|" + self.id + "}}\n"
                "|" + mwglobals.decimal_format(self.weight) + "||" + str(self.value) + "||" + mwglobals.decimal_format(self.quality))
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
            ("\n|Type|", "type"),
            ("\n|Script|", "script"),
            ("\n|Weight|    {:.2f}", "weight"),
            ("\n|Value|", "value"),
            ("\n|Quality|    {:.2f}", "quality"),
            ("\n|Model|", "model"),
            ("\n|Icon|", "icon")
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["model", "name", "type", "quality", "weight", "value", "icon", "script"])
