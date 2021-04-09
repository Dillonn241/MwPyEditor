import copy
from collections import defaultdict

from mwpyeditor.core import mwglobals
from mwpyeditor.core.mwrecord import MwRecord
from mwpyeditor.record import mwligh

init_references = False


class MwCELL(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.id_ = ''
        self.is_interior = False
        self.has_water = False
        self.illegal_to_sleep_here = False
        self.named_exterior = False
        self.behave_like_exterior = False
        self.grid_x = 0
        self.grid_y = 0
        self.region = None
        self.map_red = None
        self.map_green = None
        self.map_blue = None
        self.water_height = None
        self.ambient_red = None
        self.ambient_green = None
        self.ambient_blue = None
        self.sunlight_red = None
        self.sunlight_green = None
        self.sunlight_blue = None
        self.fog_red = None
        self.fog_green = None
        self.fog_blue = None
        self.fog_density = None
        self.nam0 = None
        self.references = []

    def load(self):
        self.id_ = self.parse_string('NAME')

        flags = self.parse_uint('DATA')
        self.is_interior = (flags & 0x1) == 0x1
        self.has_water = (flags & 0x2) == 0x2
        self.illegal_to_sleep_here = (flags & 0x4) == 0x4
        self.named_exterior = (flags & 0x40) == 0x40
        self.behave_like_exterior = (flags & 0x80) == 0x80
        self.grid_x = self.parse_int('DATA', start=4)
        self.grid_y = self.parse_int('DATA', start=8)

        self.region = self.parse_string('RGNN')

        self.map_red = self.parse_uint('NAM5', length=1)
        self.map_green = self.parse_uint('NAM5', start=1, length=1)
        self.map_blue = self.parse_uint('NAM5', start=2, length=1)

        self.water_height = self.parse_float('WHGT')

        self.ambient_red = self.parse_uint('AMBI', length=1)
        self.ambient_green = self.parse_uint('AMBI', start=1, length=1)
        self.ambient_blue = self.parse_uint('AMBI', start=2, length=1)
        self.sunlight_red = self.parse_uint('AMBI', start=4, length=1)
        self.sunlight_green = self.parse_uint('AMBI', start=5, length=1)
        self.sunlight_blue = self.parse_uint('AMBI', start=6, length=1)
        self.fog_red = self.parse_uint('AMBI', start=8, length=1)
        self.fog_green = self.parse_uint('AMBI', start=9, length=1)
        self.fog_blue = self.parse_uint('AMBI', start=10, length=1)
        self.fog_density = self.parse_float('AMBI', start=12)

        self.nam0 = self.parse_uint('NAM0')

        if init_references:
            self.load_references()

        if self.is_interior:
            if self.id_ in mwglobals.interior_cells:
                old_cell = mwglobals.interior_cells[self.id_]
                mwglobals.interior_cells[self.id_] = self.merged_references(old_cell)
            else:
                mwglobals.interior_cells[self.id_] = copy.copy(self)
                mwglobals.interior_cells[self.id_].references = copy.copy(self.references)
        else:
            grid = (self.grid_x, self.grid_y)
            if grid in mwglobals.exterior_cells:
                old_cell = mwglobals.exterior_cells[grid]
                mwglobals.exterior_cells[grid] = self.merged_references(old_cell)
            else:
                mwglobals.exterior_cells[grid] = copy.copy(self)
                mwglobals.exterior_cells[grid].references = copy.copy(self.references)

    def load_references(self):
        self.references = []
        ref = None
        mvrf = False
        for subrecord in self.ordered_subrecords:
            if subrecord.record_type == 'MVRF':
                ref = MwCELLReference()
                ref.index = subrecord.parse_uint()
                ref.moved = True
                mvrf = True
                self.references.append(ref)
            elif subrecord.record_type == 'FRMR':
                ref = MwCELLReference()
                ref.index = subrecord.parse_uint()
                mvrf = False
                self.references.append(ref)
            elif ref:
                if subrecord.record_type == 'CNDT':
                    ref.moved_grid_x = subrecord.parse_int()
                    ref.moved_grid_y = subrecord.parse_int(start=4)
                elif subrecord.record_type == 'NAME':
                    ref.id_ = subrecord.parse_string()
                elif subrecord.record_type == 'UNAM':
                    ref.blocked = True
                elif subrecord.record_type == 'XSCL':
                    ref.scale = subrecord.parse_float()
                elif subrecord.record_type == 'ANAM':
                    ref.owner = subrecord.parse_string()
                elif subrecord.record_type == 'BNAM':
                    ref.global_variable = subrecord.parse_string()
                elif subrecord.record_type == 'CNAM':
                    if mvrf:
                        ref.moved_cell = subrecord.parse_string()
                    else:
                        ref.faction = subrecord.parse_string()
                elif subrecord.record_type == 'INDX':
                    ref.faction_rank = subrecord.parse_uint()
                elif subrecord.record_type == 'XSOL':
                    ref.soul = subrecord.parse_string()
                elif subrecord.record_type == 'XCHG':
                    ref.charge_left = subrecord.parse_float()
                elif subrecord.record_type == 'INTV':
                    if isinstance(mwglobals.object_ids.get(ref.id_, None), mwligh.MwLIGH):
                        ref.uses_left = subrecord.parse_float()
                    else:
                        ref.uses_left = subrecord.parse_uint()
                elif subrecord.record_type == 'NAM9':
                    ref.stack_size = subrecord.parse_uint()
                elif subrecord.record_type == 'DODT':
                    ref.door_pos_x = subrecord.parse_float()
                    ref.door_pos_y = subrecord.parse_float(start=4)
                    ref.door_pos_z = subrecord.parse_float(start=8)
                    ref.door_rot_x = subrecord.parse_float(start=12)
                    ref.door_rot_y = subrecord.parse_float(start=16)
                    ref.door_rot_z = subrecord.parse_float(start=20)
                elif subrecord.record_type == 'DNAM':
                    ref.door_cell = subrecord.parse_string()
                elif subrecord.record_type == 'FLTV':
                    ref.lock_level = subrecord.parse_uint()
                elif subrecord.record_type == 'KNAM':
                    ref.key_id = subrecord.parse_string()
                elif subrecord.record_type == 'TNAM':
                    ref.trap_id = subrecord.parse_string()
                elif subrecord.record_type == 'DATA':
                    ref.pos_x = subrecord.parse_float()
                    ref.pos_y = subrecord.parse_float(start=4)
                    ref.pos_z = subrecord.parse_float(start=8)
                    ref.rot_x = subrecord.parse_float(start=12)
                    ref.rot_y = subrecord.parse_float(start=16)
                    ref.rot_z = subrecord.parse_float(start=20)
                elif subrecord.record_type == 'DELE':
                    ref.deleted = True

    def merged_references(self, old_cell):
        cell_copy = copy.copy(self)
        cell_copy.references = copy.copy(old_cell.references)
        for ref in self.references:
            if ref.get_master_index() == 0:
                cell_copy.references.append(ref)
            else:
                cell_copy.references = [ref if x.get_object_index() == ref.get_object_index() else
                                        x for x in cell_copy.references]
        return cell_copy

    def save(self):
        self.clear_subrecords()
        self.add_string(self.id_, 'NAME')
        sub_data = self.add_subrecord('DATA')
        flags = 0x0
        if self.is_interior:
            flags |= 0x1
        if self.has_water:
            flags |= 0x2
        if self.illegal_to_sleep_here:
            flags |= 0x4
        if self.named_exterior:
            flags |= 0x40
        if self.behave_like_exterior:
            flags |= 0x80
        sub_data.add_uint(flags)
        sub_data.add_int(self.grid_x)
        sub_data.add_int(self.grid_y)

        self.add_string(self.region, 'RGNN')
        if self.map_red:
            sub_nam5 = self.add_subrecord('NAM5')
            sub_nam5.add_uint(self.map_red, length=1)
            sub_nam5.add_uint(self.map_green, length=1)
            sub_nam5.add_uint(self.map_blue, length=1)
            sub_nam5.add_uint(0, length=1)

        self.add_float(self.water_height, 'WHGT')
        if self.ambient_red:
            sub_ambi = self.add_subrecord('AMBI')
            sub_ambi.add_uint(self.ambient_red, length=1)
            sub_ambi.add_uint(self.ambient_green, length=1)
            sub_ambi.add_uint(self.ambient_blue, length=1)
            sub_ambi.add_uint(0, length=1)
            sub_ambi.add_uint(self.sunlight_red, length=1)
            sub_ambi.add_uint(self.sunlight_green, length=1)
            sub_ambi.add_uint(self.sunlight_blue, length=1)
            sub_ambi.add_uint(0, length=1)
            sub_ambi.add_uint(self.fog_red, length=1)
            sub_ambi.add_uint(self.fog_green, length=1)
            sub_ambi.add_uint(self.fog_blue, length=1)
            sub_ambi.add_uint(0, length=1)
            sub_ambi.add_float(self.fog_density)

        def save_reference():
            self.add_uint(ref.index, 'FRMR')
            self.add_string(ref.id_, 'NAME')
            if ref.blocked:
                self.add_uint(0, 'UNAM', length=1)
            self.add_float(ref.scale, 'XSCL')
            self.add_string(ref.owner, 'ANAM')
            self.add_string(ref.global_variable, 'BNAM')
            self.add_string(ref.faction, 'CNAM')
            self.add_uint(ref.faction_rank, 'INDX')
            self.add_string(ref.soul, 'XSOL')
            self.add_float(ref.charge_left, 'XCHG')
            if isinstance(mwglobals.object_ids.get(ref.id_, None), mwligh.MwLIGH):
                self.add_float(ref.uses_left, 'INTV')
            else:
                self.add_uint(ref.uses_left, 'INTV')
            self.add_uint(ref.stack_size, 'NAM9')
            if ref.door_pos_x is not None:
                sub_dodt = self.add_subrecord('DODT')
                sub_dodt.add_float(ref.door_pos_x)
                sub_dodt.add_float(ref.door_pos_y)
                sub_dodt.add_float(ref.door_pos_z)
                sub_dodt.add_float(ref.door_rot_x)
                sub_dodt.add_float(ref.door_rot_y)
                sub_dodt.add_float(ref.door_rot_z)
            self.add_string(ref.door_cell, 'DNAM')
            self.add_uint(ref.lock_level, 'FLTV')
            self.add_string(ref.key_id, 'KNAM')
            self.add_string(ref.trap_id, 'TNAM')
            if ref.pos_x is not None:
                sub_dodt = self.add_subrecord('DATA')
                sub_dodt.add_float(ref.pos_x)
                sub_dodt.add_float(ref.pos_y)
                sub_dodt.add_float(ref.pos_z)
                sub_dodt.add_float(ref.rot_x)
                sub_dodt.add_float(ref.rot_y)
                sub_dodt.add_float(ref.rot_z)
            if ref.deleted:
                self.add_int(0, 'DELE')

        # self.references.sort(key=lambda x: (not x.is_persistent_child, x.get_master_index(), x.get_object_index()))
        num_refs = len(self.references)
        nam0 = -1
        for i in range(num_refs):
            ref = self.references[i]
            if ref.moved:
                self.add_uint(ref.index, 'MVRF')
                if ref.moved_cell:
                    self.add_string(ref.moved_cell, 'CNAM')
                if ref.moved_grid_x:
                    sub_cndt = self.add_subrecord('CNDT')
                    sub_cndt.add_int(ref.moved_grid_x)
                    sub_cndt.add_int(ref.moved_grid_y)
            elif nam0 == -1 and not ref.is_persistent_child():
                nam0 = num_refs - i
                self.add_uint(nam0, 'NAM0')
            save_reference()
        self.save_deleted()

    def get_region(self):
        if not self.is_interior and self.region is None:
            return "Wilderness"
        return self.region

    def get_name(self):
        if self.id_ or self.is_interior:
            return self.id_
        return self.region

    def get_coords(self):
        return f"[{self.grid_x},{self.grid_y}]"

    def record_details(self):
        string = [MwRecord.format_record_details(self, [
            ("|Name|", '__str__'),
            ("\n|Has Water|", 'has_water', True if not self.is_interior else False),
            ("\n|Illegal to Sleep Here|", 'illegal_to_sleep_here', False),
            ("\n|Behave Like Exterior|", 'behave_like_exterior', False),
            ("\n|Region|", 'region'),
            ("\n|Map RGB|", 'map_red'), (", {}", 'map_green'), (", {}", 'map_blue'),
            ("\n|Water Height|", 'water_height', 0 if self.is_interior else None),
            ("\n|Ambient RGB|", 'ambient_red'), (", {}", 'ambient_green'), (", {}", 'ambient_blue'),
            ("\n|Sunlight RGB|", 'sunlight_red'), (", {}", 'sunlight_green'), (", {}", 'sunlight_blue'),
            ("\n|Fog RGB|", 'fog_red'), (", {}", 'fog_green'), (", {}", 'fog_blue'), ("    |Density|", 'fog_density')
        ])]
        if init_references:
            for ref in self.references:
                string.append(f"\n{ref.record_details()}")
        elif 'FRMR' in self.subrecords:
            string.append("\nHas References")
        return ''.join(string)

    def __str__(self):
        if self.is_interior:
            return self.id_
        if self.id_:
            return f"{self.id_} {self.get_coords()}"
        return f"{self.region} {self.get_coords()}"

    def get_id(self):
        return str(self)

    def diff_old(self, other):
        diff = [MwRecord.diff(self, other, ['has_water', 'illegal_to_sleep_here', 'behave_like_exterior', 'region',
                                            'map_red', 'map_green', 'map_blue', 'water_height', 'ambient_red',
                                            'ambient_green', 'ambient_blue', 'sunlight_red', 'sunlight_green',
                                            'sunlight_blue', 'fog_red', 'fog_green', 'fog_blue', 'fog_density'])]

        ref_details1 = [ref.diff_string() for ref in self.references]
        ref_details2 = [ref.diff_string() for ref in other.references]

        for ref2 in ref_details2:
            if ref2 not in ref_details1:
                diff.append(f"\n{self}: Added {ref2}")

        for ref1 in ref_details1:
            if ref1 not in ref_details2:
                diff.append(f"\n{self}: Removed {ref1}")

        return ''.join(diff)

    def diff(self, other):
        # Like diff_old, but trying to match changed references (for now, only if
        # at a distance of < 200 and with the same ID).
        diff = [MwRecord.diff(self, other, ['has_water', 'illegal_to_sleep_here', 'behave_like_exterior', 'region',
                                            'map_red', 'map_green', 'map_blue', 'water_height', 'ambient_red',
                                            'ambient_green', 'ambient_blue', 'sunlight_red', 'sunlight_green',
                                            'sunlight_blue', 'fog_red', 'fog_green', 'fog_blue', 'fog_density'])]

        different = False

        refs1 = defaultdict(list)
        refs2 = defaultdict(list)
        refids = []

        for ref in self.references:
            refs1[ref.id_].append(ref)
            if ref.id_ not in refids:
                refids.append(ref.id_)
        for ref in other.references:
            refs2[ref.id_].append(ref)
            if ref.id_ not in refids:
                refids.append(ref.id_)

        for refid in refids:
            # Form the set of differences between refs1[refid] and refs2[refid]:
            refs1_refid_strings = [ref1.diff_string() for ref1 in refs1[refid]]
            refs2_refid_strings = [ref2.diff_string() for ref2 in refs2[refid]]
            refs1only = [ref1 for ref1 in refs1[refid] if
                         ref1.diff_string() not in refs2_refid_strings]
            refs2only = [ref2 for ref2 in refs2[refid] if
                         ref2.diff_string() not in refs1_refid_strings]

            if not different:
                if refs1only or refs2only:
                    different = True
                    diff.append(f"\n### Cell {self}: ###\n")

            for ref1 in refs1only:
                # Try to match ref1 with a reference from other that has
                # the same ID and is close by.
                distance_cutoff = 200
                closest_dist = distance_cutoff
                closest_ref = None
                for ref2 in refs2only:
                    dist = ref1.distance(ref2)
                    if dist < closest_dist:
                        closest_ref = ref2
                        closest_dist = dist
                if closest_dist < distance_cutoff:
                    ref1.diff(closest_ref)
                    refs1only.remove(ref1)
                    refs2only.remove(closest_ref)

            for ref2 in refs2only:
                diff.append(f"\nAdded {ref2}")

            for ref1 in refs1only:
                diff.append(f"\nRemoved {ref1}")

            return ''.join(diff)


class MwCELLReference:
    diff_list = ['scale', 'owner', 'global_variable', 'faction', 'faction_rank', 'soul', 'charge_left', 'uses_left',
                 'door_pos_x', 'door_pos_y', 'door_pos_z', 'door_rot_x', 'door_rot_y', 'door_rot_z', 'door_cell',
                 'lock_level', 'key_id', 'trap_id', 'pos_x', 'pos_y', 'pos_z', 'rot_x', 'rot_y', 'rot_z']

    def __init__(self):
        self.moved = None
        self.index = 0
        self.moved_grid_x = None
        self.moved_grid_y = None
        self.id_ = ''
        self.blocked = False
        self.scale = None
        self.owner = None
        self.global_variable = None
        self.moved_cell = None
        self.faction = None
        self.faction_rank = None
        self.soul = None
        self.charge_left = None
        self.uses_left = None
        self.stack_size = None
        self.door_pos_x = None
        self.door_pos_y = None
        self.door_pos_z = None
        self.door_rot_x = None
        self.door_rot_y = None
        self.door_rot_z = None
        self.door_cell = None
        self.lock_level = None
        self.key_id = None
        self.trap_id = None
        self.pos_x = None
        self.pos_y = None
        self.pos_z = None
        self.rot_x = None
        self.rot_y = None
        self.rot_z = None
        self.deleted = False

    def is_persistent_child(self):
        if self.door_cell or self.door_pos_x:
            return True
        obj = mwglobals.object_ids[self.id_]
        if obj.persists:
            return True
        obj_record_type = obj.get_record_type()
        if obj_record_type == 'CREA' or obj_record_type == 'NPC_':
            return True
        return False

    def get_object_index(self):
        return self.index & 0xFFFFFF

    def get_master_index(self):
        return self.index >> 24

    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", "id_"), ("    |Object Index|", 'get_object_index'), ("    |Master Index|", 'get_master_index'),
            ("\n  |Scale|    {:.2f}", 'scale'),
            ("\n  |Owner|", 'owner'), ("    |Global Variable|", 'global_variable'),
            ("\n  |Faction|", 'faction'), ("    |Rank|", 'faction_rank'),
            ("\n  |Soul|", 'soul'),
            ("\n  |Charge Left|", 'charge_left'),
            ("\n  |Uses Left|", 'uses_left'),
            ("\n  |Door|    {:.3f}", 'door_pos_x'), (", {:.3f}", 'door_pos_y'), (", {:.3f}", 'door_pos_z'),
            (" [{:.3f}", 'door_rot_x'), (", {:.3f}", 'door_rot_y'), (", {:.3f}]", 'door_rot_z'), (" {}", 'door_cell'),
            ("\n  |Lock|", 'lock_level'),
            ("\n  |Key|", 'key_id'),
            ("\n  |Trap|", 'trap_id'),
            ("\n  |Position|    {:.3f}", 'pos_x'), (", {:.3f}", 'pos_y'), (", {:.3f}", 'pos_z'), (" [{:.3f}", 'rot_x'),
            (", {:.3f}", 'rot_y'), (", {:.3f}]", 'rot_z')
        ])

    def __str__(self):
        if self.pos_x:
            return f"{self.id_} ({self.pos_x:.3f}, {self.pos_y:.3f}, {self.pos_z:.3f})"
        return self.id_

    def __repr__(self):
        return str(self)

    def diff(self, other):
        return MwRecord.diff(self, other, MwCELLReference.diff_list)

    def diff_string(self):
        return ''.join(str(getattr(self, attr, '')) for attr in MwCELLReference.diff_list)

    def distance(self, other):
        # taxicab distance
        return abs(self.pos_x - other.pos_x) + abs(self.pos_y - other.pos_y) + abs(self.pos_z - other.pos_z)
