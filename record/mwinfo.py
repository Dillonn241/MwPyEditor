from mwrecord import MwRecord
import mwglobals

class MwINFO(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("INAM")
        self.prev_id = self.get_subrecord_string("PNAM")
        self.next_id = self.get_subrecord_string("NNAM")
        self.response = self.get_subrecord_string("NAME")
        self.disposition = self.get_subrecord_int("DATA", start=4, length=4)
        self.rank = self.get_subrecord_int("DATA", start=8, length=1)
        self.sex = self.get_subrecord_int("DATA", start=9, length=1)
        self.pc_rank = self.get_subrecord_int("DATA", start=10, length=1)
        self.actor = self.get_subrecord_string("ONAM")
        self.race = self.get_subrecord_string("RNAM")
        self.class_ = self.get_subrecord_string("CNAM")
        self.faction = self.get_subrecord_string("FNAM")
        self.cell = self.get_subrecord_string("ANAM")
        self.pc_faction = self.get_subrecord_string("DNAM")
        self.sound_file = self.get_subrecord_string("SNAM")
        self.quest_name = self.get_subrecord_int("QSTN") == 1
        self.quest_finished = self.get_subrecord_int("QSTF") == 1
        self.quest_restart = self.get_subrecord_int("QSTR") == 1
        self.func_var_filters = []
        for i in range(self.num_subrecords("SCVR")):
            func_var_filter = MwINFOFilter()
            func_var_filter.type = self.get_subrecord_int("SCVR", index=i, start=1, length=1) - 48
            if func_var_filter.type > 9:
                func_var_filter.type -= 7
            func_var_filter.function = self.get_subrecord_string("SCVR", index=i, start=2, length=2)
            func_var_filter.compare = self.get_subrecord_int("SCVR", index=i, start=4, length=1) - 48
            func_var_filter.name = self.get_subrecord_string("SCVR", index=i, start=5)
            func_var_filter.intv = 0
            self.func_var_filters += [func_var_filter]
        for i in range(self.num_subrecords("INTV")):
            self.func_var_filters[i].intv = self.get_subrecord_int("INTV", index=i)
        self.result = self.get_subrecord_string("BNAM")
        mwglobals.info_ids[self.id] = self
    
    def save(self):
        self.set_subrecord_string(self.id, "INAM")
        self.set_subrecord_string(self.prev_id, "PNAM")
        self.set_subrecord_string(self.next_id, "NNAM")
    
    def record_details(self, full=False):
        if self.dial.type == "Journal":
            disp_index = "Index"
            response_entry = "Entry"
        else:
            disp_index = "Disp"
            response_entry = "Response"
        string = MwRecord.format_record_details(self, [
        ("|ID|", "id"), ("    |Prev|", "prev_id", ""), ("    |Next|", "next_id", "")
        ]) + "\n" if full else ""
        return string + MwRecord.format_record_details(self, [
        ("|" + response_entry + "|", "response"),
        ("\n|" + disp_index + "|", "disposition", 0),
        ("\n|Sex|", "sex", -1),
        ("\n|Actor|", "actor"),
        ("\n|Race|", "race"),
        ("\n|Class|", "class_"),
        ("\n|Faction|", "faction"), ("    |Rank|", "rank", -1),
        ("\n|Cell|", "cell"),
        ("\n|PC Faction|", "pc_faction"), ("    |PC Rank|", "pc_rank", -1),
        ("\n|Sound Filename|", "sound_file"),
        ("\n|Quest Name|", "quest_name", False),
        ("\n|Quest Finished|", "quest_finished", False),
        ("\n|Quest Restart|", "quest_restart", False),
        ("\n|Function/Variable|", "func_var_filters", []),
        ("\n|Result|", "result")
        ])
    
    def __str__(self):
        return "{}: {} [{}]".format(self.dial, self.response, self.id)
    
    def __repr__(self):
        return str(self)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["prev_id", "next_id", "response", "disposition", "rank", "sex", "pc_rank", "actor", "race", "class_", "faction", "cell", "pc_faction", "sound_file", "quest_name", "quest_finished", "quest_restart", "func_var_filters", "result"])

class MwINFOFilter:
    def get_type_string(self):
        return mwglobals.INFO_SCVR_TYPE[self.type]
    
    def get_function_string(self):
        if self.function[1] == "X":
            return self.name
        return mwglobals.INFO_SCVR_FUNCTION[int(self.function)]
    
    def get_compare_string(self):
        return mwglobals.INFO_SCVR_COMPARE[self.compare]
    
    def __str__(self):
        return self.get_type_string() + " " + self.get_function_string() + " " + self.get_compare_string() + " " + str(self.intv)
    
    def __repr__(self):
        return str(self)