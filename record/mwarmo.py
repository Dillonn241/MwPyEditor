from mwrecord import MwRecord
import mwglobals

class MwARMO(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        self.model = self.get_subrecord_string("MODL")
        self.name = self.get_subrecord_string("FNAM")
        self.script = self.get_subrecord_string("SCRI")
        self.type = mwglobals.ARMO_TYPES[self.get_subrecord_int("AODT", start=0, length=4)]
        self.weight = self.get_subrecord_float("AODT", start=4, length=4)
        self.value = self.get_subrecord_int("AODT", start=8, length=4)
        self.health = self.get_subrecord_int("AODT", start=12, length=4)
        self.enchantment = self.get_subrecord_int("AODT", start=16, length=4)
        self.armor = self.get_subrecord_int("AODT", start=20, length=4)
        self.icon = self.get_subrecord_string("ITEX")
        self.enchanting = self.get_subrecord_string("ENAM")
        mwglobals.object_ids[self.id] = self
        
        load_body_parts(self)
    
    def is_pauldron(self):
        return self.type == "Left Pauldron" or self.type == "Right Pauldron"
    
    def is_bracer(self):
        return self.type == "Left Bracer" or self.type == "Right Bracer"
    
    def is_gauntlet(self):
        return self.type == "Left Gauntlet" or self.type == "Right Gauntlet"
    
    def is_bracer_or_gauntlet(self):
        return self.is_bracer() or self.is_gauntlet()
    
    def get_weight_class(self):
        if self.type == "Helmet":
            weight_setting = 5 # iHelmWeight
        elif self.type == "Cuirass":
            weight_setting = 30 # iCuirassWeight"
        elif self.is_pauldron():
            weight_setting = 10 # iPauldronWeight
        elif self.type == "Greaves":
            weight_setting = 15 # iGreavesWeight
        elif self.type == "Boots":
            weight_setting = 20 # iBootsWeight
        elif self.type == "Shield":
            weight_setting = 15 # iShieldWeight
        else:
            weight_setting = 5 # iGauntletWeight
        epsilon = 0.0005
        if self.weight <= weight_setting * 0.6 + epsilon: # fLightMaxMod
            return "Light"
        elif self.weight <= weight_setting * 0.9 + epsilon: # fMedMaxMod
            return "Medium"
        else:
            return "Heavy"
    
    def record_details(self):
        return "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Type|", "type"),
        ("\n|Script|", "script"),
        ("\n|Weight|    {:.2f}", "weight"), (" ({})", self.get_weight_class(), None, None),
        ("\n|Value|", "value"),
        ("\n|AR|", "armor"),
        ("\n|Health|", "health"),
        ("\n|Model|", "model"),
        ("\n|Icon|", "icon"),
        ("\n|Enchantment|", "enchantment"),
        ("\n|Enchanting|", "enchanting"),
        ("\n|Body Parts|", "body_parts")
        ])
    
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    
    def diff(self, other):
        MwRecord.diff(self, other, ["model", "name", "script", "type", "weight", "value", "health", "enchantment", "armor", "icon", "body_parts", "enchanting"])

def load_body_parts(self):
    self.body_parts = []
    body_part = None
    for subrecord in self.ordered_subrecords:
        if subrecord.record_type == "INDX":
            if body_part != None:
                self.body_parts += [body_part]
            body_part = MwARMOBodyPart()
            body_part.type = mwglobals.ARMO_PARTS[subrecord.get_int()]
            body_part.male_name = None
            body_part.female_name = None
        elif subrecord.record_type == "BNAM":
            body_part.male_name = subrecord.get_string()
        elif subrecord.record_type == "CNAM":
            body_part.female_name = subrecord.get_string()
    if body_part != None:
        self.body_parts += [body_part]

class MwARMOBodyPart:
    def __str__(self):
        string = "{}:".format(self.type)
        if self.male_name != None:
            string += " {} (Male)".format(self.male_name)
        if self.female_name != None:
            string += " {} (Female)".format(self.female_name)
        return string
    
    def __repr__(self):
        return str(self)