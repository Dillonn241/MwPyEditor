from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord


class MwINGR(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.model = ''
        self.name = None
        self.weight = 0.0
        self.value = 0
        self.effect_ids = []
        self.script = None
        self.icon = None

    def load(self):
        self.id_ = self.parse_string('NAME')
        self.model = self.parse_string('MODL')
        self.name = self.parse_string('FNAM')

        self.weight = self.parse_float('IRDT')
        self.value = self.parse_uint('IRDT', start=4)
        self.effect_ids = [(self.parse_int('IRDT', start=8 + i * 4),  # effect_id
                            self.parse_int('IRDT', start=24 + i * 4),  # skill_id
                            self.parse_int('IRDT', start=40 + i * 4))  # attribute_id
                           for i in range(4)]

        self.script = self.parse_string('SCRI')
        self.icon = self.parse_string('ITEX')

        mwglobals.object_ids[self.id_] = self

    def get_effects(self):
        return [self.get_effect(i) for i in range(4)]

    def set_effects(self, effect_tuples):
        for i in range(len(self.effect_ids)):
            self.set_effect(effect_tuples[i], i)

    def get_effect(self, index):
        effect_id = self.effect_ids[index][0]
        skill_id = self.effect_ids[index][1]
        attribute_id = self.effect_ids[index][2]
        return (mwglobals.MAGIC_NAMES[effect_id] if effect_id != -1 else None,
                mwglobals.SKILLS[skill_id] if skill_id != -1 else None,
                mwglobals.ATTRIBUTES[attribute_id] if attribute_id != -1 else None)

    def set_effect(self, effect_tuple, index):
        effect_id = mwglobals.MAGIC_NAMES.index(effect_tuple[0]) if effect_tuple[0] in mwglobals.MAGIC_NAMES else -1
        skill_id = mwglobals.SKILLS.index(effect_tuple[1]) if effect_tuple[1] in mwglobals.SKILLS else -1
        attribute_id = mwglobals.ATTRIBUTES.index(effect_tuple[2]) if effect_tuple[2] in mwglobals.ATTRIBUTES else -1
        self.effect_ids[index] = (effect_id, skill_id, attribute_id)

    def record_details(self):
        string = [MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Model|", 'model'),
            ("\n|Weight|    {:.2f}", 'weight'),
            ("\n|Value|", 'value'),
            ("\n|Script|", 'script'),
            ("\n|Icon|", 'icon')
        ])]
        for i in range(len(self.effect_ids)):
            effect_id = self.effect_ids[i][0]
            if effect_id != -1:
                string.append(f"\n|Effect {i + 1}|    {mwglobals.MAGIC_NAMES[effect_id]}")
                skill_id = self.effect_ids[i][1]
                attribute_id = self.effect_ids[i][2]
                if skill_id != -1:
                    string.append(f" {skill_id}")
                elif attribute_id != -1:
                    string.append(f" {attribute_id}")
        return ''.join(string)

    def __str__(self):
        return f"{self.name} [{self.id_}]"

    def diff(self, other):
        return MwRecord.diff(self, other, ['model', 'name', 'weight', 'value', 'get_effects', 'script', 'icon'])
