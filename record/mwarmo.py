import mwglobals
from mwrecord import MwRecord


class MwARMO(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = ''
        self.script = None
        self.type_id = 0
        self.weight = 0.0
        self.value = 0
        self.health = 0
        self.enchantment = 0
        self.armor = 0
        self.icon = None
        self.body_parts = []
        self.enchanting = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')
        self.script = self.parse_string('SCRI')

        self.type_id = self.parse_uint('AODT')
        self.weight = self.parse_float('AODT')
        self.value = self.parse_uint('AODT', start=8)
        self.health = self.parse_uint('AODT', start=12)
        self.enchantment = self.parse_uint('AODT', start=16)
        self.armor = self.parse_uint('AODT', start=20)

        self.icon = self.parse_string('ITEX')

        load_body_parts(self)

        self.enchanting = self.parse_string('ENAM')

        mwglobals.object_ids[self.id_] = self

    def get_type(self):
        if 0 <= self.type_id < len(mwglobals.ARMO_TYPES):
            return mwglobals.ARMO_TYPES[self.type_id]

    def set_type(self, value):
        if value in mwglobals.ARMO_TYPES:
            self.type_id = mwglobals.ARMO_TYPES.index(value)

    def is_pauldron(self):
        return self.type_id == 2 or self.type_id == 3  # Left Pauldron or Right Pauldron

    def is_gauntlet(self):
        return self.type_id == 6 or self.type_id == 7  # Left Gauntlet or Right Gauntlet

    def is_bracer(self):
        return self.type_id == 9 or self.type_id == 10  # Left Bracer or Right Bracer

    def is_gauntlet_or_bracer(self):
        return self.is_gauntlet() or self.is_bracer()

    def get_weight_class(self):
        if self.type_id == 0:  # Helmet
            weight_setting = 5  # iHelmWeight
        elif self.type_id == 1:  # Cuirass
            weight_setting = 30  # iCuirassWeight"
        elif self.is_pauldron():  # Pauldrons
            weight_setting = 10  # iPauldronWeight
        elif self.type_id == 4:  # Greaves
            weight_setting = 15  # iGreavesWeight
        elif self.type_id == 5:  # Boots
            weight_setting = 20  # iBootsWeight
        elif self.type_id == 8:  # Shield
            weight_setting = 15  # iShieldWeight
        else:  # Gauntlets or Bracers
            weight_setting = 5  # iGauntletWeight
        epsilon = 0.0005
        if self.weight <= weight_setting * 0.6 + epsilon:  # 0.6 = fLightMaxMod
            return "Light"
        elif self.weight <= weight_setting * 0.9 + epsilon:  # 0.9 = fMedMaxMod
            return "Medium"
        else:
            return "Heavy"

    def get_actual_enchantment(self):
        return self.enchantment / 10

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Model|", 'model'),
            ("\n|Script|", 'script'),
            ("\n|Type|", 'get_type'),
            ("\n|Weight|    {:.2f}", 'weight'), (" ({})", 'get_weight_class'),
            ("\n|Value|", 'value'),
            ("\n|Health|", 'health'),
            ("\n|Enchantment|", 'enchantment'),
            ("\n|Armor|", 'armor'),
            ("\n|Icon|", 'icon'),
            ("\n|Body Parts|", 'body_parts'),
            ("\n|Enchanting|", 'enchanting')
        ])

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'script', 'get_type', 'weight', 'value', 'health',
                                           'enchantment', 'armor', 'icon', 'body_parts', 'enchanting'])


def load_body_parts(self):
    self.body_parts = []
    body_part = None
    for subrecord in self.ordered_subrecords:
        if subrecord.record_type == 'INDX':
            body_part = MwARMOBodyPart()
            body_part.type_id = subrecord.parse_uint()
            self.body_parts += [body_part]
        elif subrecord.record_type == 'BNAM':
            body_part.male_name = subrecord.parse_string()
        elif subrecord.record_type == 'CNAM':
            body_part.female_name = subrecord.parse_string()


class MwARMOBodyPart:
    def __init__(self):
        self.type_id = 0
        self.male_name = None
        self.female_name = None

    def get_type(self):
        if 0 <= self.type_id < len(mwglobals.ARMO_PARTS):
            return mwglobals.ARMO_PARTS[self.type_id]

    def set_type(self, value):
        if value in mwglobals.ARMO_PARTS:
            self.type_id = mwglobals.ARMO_PARTS.index(value)

    def __str__(self):
        string = [f"{self.get_type()}:"]
        if self.male_name:
            string.append(f" {self.male_name} (Male)")
        if self.female_name:
            string.append(f" {self.female_name} (Female)")
        return ''.join(string)

    def __repr__(self):
        return str(self)
