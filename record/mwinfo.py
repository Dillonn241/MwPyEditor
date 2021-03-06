import mwglobals
from mwrecord import MwRecord


class MwINFO(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("INAM")
        self.prev_id = self.get_subrecord_string("PNAM")
        self.next_id = self.get_subrecord_string("NNAM")
        self.disposition = self.get_subrecord_uint("DATA", start=4, length=4)
        self.rank = self.get_subrecord_uint("DATA", start=8, length=1)
        self.sex = self.get_subrecord_int("DATA", start=9, length=1)
        self.pc_rank = self.get_subrecord_uint("DATA", start=10, length=1)
        self.actor = self.get_subrecord_string("ONAM")
        self.race = self.get_subrecord_string("RNAM")
        self.class_ = self.get_subrecord_string("CNAM")
        self.faction = self.get_subrecord_string("FNAM")
        self.cell = self.get_subrecord_string("ANAM")
        self.pc_faction = self.get_subrecord_string("DNAM")
        self.sound_file = self.get_subrecord_string("SNAM")
        self.response = self.get_subrecord_string("NAME")
        self.func_var_filters = []
        func_var_filter = None
        for subrecord in self.ordered_subrecords:
            if subrecord.record_type == "SCVR":
                func_var_filter = MwINFOFilter()
                func_var_filter.index = subrecord.get_int(start=0, length=1) - 48
                func_var_filter.type = subrecord.get_int(start=1, length=1) - 48
                if func_var_filter.type > 9:
                    func_var_filter.type -= 7
                func_var_filter.function = subrecord.get_string(start=2, length=2)
                func_var_filter.operator = subrecord.get_int(start=4, length=1) - 48
                func_var_filter.name = subrecord.get_string(start=5)
                self.func_var_filters += [func_var_filter]
            elif subrecord.record_type == "INTV":
                func_var_filter.intv = subrecord.get_uint()
            elif subrecord.record_type == "FLTV":
                func_var_filter.fltv = subrecord.get_float()
        self.result = self.get_subrecord_string("BNAM")
        self.quest_name = self.get_subrecord_int("QSTN") == 1
        self.quest_finished = self.get_subrecord_int("QSTF") == 1
        self.quest_restart = self.get_subrecord_int("QSTR") == 1
        mwglobals.info_ids[self.id] = self
    
    def save(self):
        self.clear_subrecords()
        self.add_subrecord_string(self.id, "INAM")
        self.add_subrecord_string(self.prev_id, "PNAM")
        self.add_subrecord_string(self.next_id, "NNAM")
        if not self.deleted:
            sub_data = self.add_subrecord("DATA")
            sub_data.add_uint(self.dial.get_type_index(), length=1)
            sub_data.data += b"\x00\x00\x00"
            sub_data.add_uint(self.disposition)
            sub_data.add_uint(self.rank, length=1)
            sub_data.add_int(self.sex, length=1)
            sub_data.add_uint(self.pc_rank, length=1)
            sub_data.data += b"\x00"
            self.add_subrecord_string(self.actor, "ONAM")
            self.add_subrecord_string(self.race, "RNAM")
            self.add_subrecord_string(self.class_, "CNAM")
            self.add_subrecord_string(self.faction, "FNAM")
            self.add_subrecord_string(self.cell, "ANAM")
            self.add_subrecord_string(self.pc_faction, "DNAM")
            self.add_subrecord_string(self.sound_file, "SNAM")
        self.add_subrecord_string(self.response, "NAME", terminator=False)
        if not self.deleted:
            for func_var_filter in self.func_var_filters:
                sub_scvr = self.add_subrecord("SCVR")
                sub_scvr.add_int(func_var_filter.index + 48, length=1)
                func_type = func_var_filter.type
                if func_type > 9:
                    func_type += 7
                sub_scvr.add_int(func_type + 48, length=1)
                sub_scvr.add_string(func_var_filter.function, terminator=False)
                sub_scvr.add_int(func_var_filter.operator + 48, length=1)
                sub_scvr.add_string(func_var_filter.name, terminator=False)
                if hasattr(func_var_filter, "intv"):
                    self.add_subrecord_uint(func_var_filter.intv, "INTV")
                elif hasattr(func_var_filter, "fltv"):
                    self.add_subrecord_float(func_var_filter.fltv, "FLTV")
            self.add_subrecord_string(self.result, "BNAM", terminator=False)
            if self.quest_name:
                self.add_subrecord_int(1, "QSTN", length=1)
            elif self.quest_finished:
                self.add_subrecord_int(1, "QSTF", length=1)
            elif self.quest_restart:
                self.add_subrecord_int(1, "QSTR", length=1)
    
    def filter(self, actor="", race="", class_="", faction="", cell="", pc_faction=""):
        if actor != "" and actor != self.actor:
            return False
        if race != "" and race != self.race:
            return False
        if class_ != "" and class_ != self.class_:
            return False
        if faction != "" and faction != self.faction:
            return False
        if cell != "" and not (self.cell and self.cell.startswith(cell)):
            return False
        if pc_faction != "" and pc_faction != self.pc_faction:
            return False
        return True
    
    def record_details(self):
        if self.dial.type == "Journal":
            disp_index = "Index"
            response_entry = "Entry"
        else:
            disp_index = "Disp"
            response_entry = "Response"
        return MwRecord.format_record_details(self, [
            ("|" + response_entry + "|    " + str(self.dial) + ": {}", "response"),
            ("\n|ID|", "id"), ("    |Prev|", "prev_id", ""), ("    |Next|", "next_id", ""),
            ("\n|" + disp_index + "|", "disposition", 0),
            ("\n|Sex|", "sex", -1),
            ("\n|Actor|", "actor"),
            ("\n|Race|", "race"),
            ("\n|Class|", "class_"),
            ("\n|Faction|", "faction"), ("    |Rank|", "rank", -1),
            ("\n|Cell|", "cell"),
            ("\n|PC Faction|", "pc_faction"), ("    |PC Rank|", "pc_rank", -1),
            ("\n|Sound Filename|", "sound_file"),
            ("\n|Function/Variable|", "func_var_filters", []),
            ("\n|Result|", "result"),
            ("\n|Quest Name|", "quest_name", False),
            ("\n|Quest Finished|", "quest_finished", False),
            ("\n|Quest Restart|", "quest_restart", False)
        ])
    
    def __str__(self):
        return "{}: {} [{}]".format(self.dial, self.response, self.id)
    
    def __repr__(self):
        return str(self)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["prev_id", "next_id", "disposition", "rank", "sex", "pc_rank", "actor", "race",
                                    "class_", "faction", "cell", "pc_faction", "sound_file", "response",
                                    "func_var_filters", "result", "quest_name", "quest_finished", "quest_restart"])


class MwINFOFilter:
    def get_type_string(self):
        return mwglobals.INFO_SCVR_TYPE[self.type]
    
    def get_function_string(self):
        if self.function[1] == "X":
            return self.name
        return mwglobals.INFO_SCVR_FUNCTION[int(self.function)]
    
    def get_operator_string(self):
        return mwglobals.INFO_SCVR_OPERATOR[self.operator]
    
    def get_value_string(self):
        if hasattr(self, "intv"):
            return str(self.intv)
        elif hasattr(self, "fltv"):
            return str(self.fltv)
    
    def __str__(self):
        return self.get_type_string() + " " + self.get_function_string() + " " + self.get_operator_string() + " " + self.get_value_string()
    
    def __repr__(self):
        return str(self)
