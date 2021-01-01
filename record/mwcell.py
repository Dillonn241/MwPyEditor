from collections import defaultdict
import copy

import mwglobals
from mwrecord import MwRecord
import record.mwligh as mwligh

init_references = False

class MwCELL(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.references_loaded = False
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        
        flags = self.get_subrecord_int("DATA", start=0, length=4)
        self.is_interior = (flags & 0x1) == 0x1
        self.has_water = (flags & 0x2) == 0x2
        self.illegal_to_sleep_here = (flags & 0x4) == 0x4
        self.behave_like_exterior = (flags & 0x8) == 0x8
        self.grid_x = self.get_subrecord_int("DATA", start=4, length=4)
        self.grid_y = self.get_subrecord_int("DATA", start=8, length=4)
        
        self.water_height = self.get_subrecord_float("WHGT")
        self.ambient_red = self.get_subrecord_int("AMBI", start=0, length=1, signed=False)
        self.ambient_green = self.get_subrecord_int("AMBI", start=1, length=1, signed=False)
        self.ambient_blue = self.get_subrecord_int("AMBI", start=2, length=1, signed=False)
        self.sunlight_red = self.get_subrecord_int("AMBI", start=4, length=1, signed=False)
        self.sunlight_green = self.get_subrecord_int("AMBI", start=5, length=1, signed=False)
        self.sunlight_blue = self.get_subrecord_int("AMBI", start=6, length=1, signed=False)
        self.fog_red = self.get_subrecord_int("AMBI", start=8, length=1, signed=False)
        self.fog_green = self.get_subrecord_int("AMBI", start=9, length=1, signed=False)
        self.fog_blue = self.get_subrecord_int("AMBI", start=10, length=1, signed=False)
        self.fog_density = self.get_subrecord_float("AMBI", start=12, length=4)
        
        self.region = self.get_subrecord_string("RGNN")
        if self.region is None:
            self.region = "Wilderness"
        self.map_red = self.get_subrecord_int("NAM5", start=0, length=1, signed=False)
        self.map_green = self.get_subrecord_int("NAM5", start=1, length=1, signed=False)
        self.map_blue = self.get_subrecord_int("NAM5", start=2, length=1, signed=False)
        
        if init_references:
            self.load_references()
        
        if self.is_interior:
            if self.id not in mwglobals.interior_cells:
                mwglobals.interior_cells[self.id] = copy.copy(self)
                if self.references_loaded:
                    mwglobals.interior_cells[self.id].references = copy.copy(self.references)
        else:
            grid = (self.grid_x, self.grid_y)
            if grid not in mwglobals.exterior_cells:
                mwglobals.exterior_cells[grid] = copy.copy(self)
                if self.references_loaded:
                    mwglobals.exterior_cells[grid].references = copy.copy(self.references)
    
    def load_references(self):
        self.references = []
        reference = None
        for subrecord in self.ordered_subrecords:
            if subrecord.record_type == "FRMR":
                reference = MwCELLReference()
                reference.index = subrecord.get_int()
                self.references += [reference]
            elif reference != None:
                if subrecord.record_type == "NAME":
                    reference.id = subrecord.get_string()
                elif subrecord.record_type == "UNAM":
                    reference.blocked = True
                elif subrecord.record_type == "XSCL":
                    reference.scale = subrecord.get_float()
                elif subrecord.record_type == "ANAM":
                    reference.owner = subrecord.get_string()
                elif subrecord.record_type == "BNAM":
                    reference.global_variable = subrecord.get_string()
                elif subrecord.record_type == "CNAM":
                    reference.faction = subrecord.get_string()
                elif subrecord.record_type == "INDX":
                    reference.faction_rank = subrecord.get_string()
                elif subrecord.record_type == "XSOL":
                    reference.soul = subrecord.get_string()
                elif subrecord.record_type == "XCHG":
                    reference.charge_left = subrecord.get_float()
                elif subrecord.record_type == "INTV":
                    if reference.id in mwglobals.object_ids and isinstance(mwglobals.object_ids[reference.id], mwligh.MwLIGH):
                        reference.uses_left = subrecord.get_float()
                    else:
                        reference.uses_left = subrecord.get_int()
                elif subrecord.record_type == "DODT":
                    reference.door_pos_x = subrecord.get_float(start=0, length=4)
                    reference.door_pos_y = subrecord.get_float(start=4, length=4)
                    reference.door_pos_z = subrecord.get_float(start=8, length=4)
                    reference.door_rot_x = subrecord.get_float(start=12, length=4)
                    reference.door_rot_y = subrecord.get_float(start=16, length=4)
                    reference.door_rot_z = subrecord.get_float(start=20, length=4)
                elif subrecord.record_type == "DNAM":
                    reference.door_cell = subrecord.get_string()
                elif subrecord.record_type == "FLTV":
                    reference.lock_level = subrecord.get_int()
                elif subrecord.record_type == "KNAM":
                    reference.key_id = subrecord.get_string()
                elif subrecord.record_type == "TNAM":
                    reference.trap_id = subrecord.get_string()
                elif subrecord.record_type == "DATA":
                    reference.pos_x = subrecord.get_float(start=0, length=4)
                    reference.pos_y = subrecord.get_float(start=4, length=4)
                    reference.pos_z = subrecord.get_float(start=8, length=4)
                    reference.rot_x = subrecord.get_float(start=12, length=4)
                    reference.rot_y = subrecord.get_float(start=16, length=4)
                    reference.rot_z = subrecord.get_float(start=20, length=4)
                elif subrecord.record_type == "DELE":
                    reference.deleted = True
        
        if self.is_interior:
            if self.id in mwglobals.interior_cells:
                self.update_references(mwglobals.interior_cells, self.id)
        else:
            grid = (self.grid_x, self.grid_y)
            if grid in mwglobals.exterior_cells:
                self.update_references(mwglobals.exterior_cells, grid)
        
        self.references_loaded = True
    
    def update_references(self, cell_list, id):
        cell_copy = copy.copy(self)
        cell_copy.references = cell_list[id].references
        for ref in self.references:
            if ref.get_master_index() == 0:
                cell_copy.references += [ref]
            else:
                cell_copy.references = [ref if x.get_object_index() == ref.get_object_index() else x for x in cell_copy.references]
        cell_list[id] = cell_copy
    
    def save(self):
        self.set_subrecord_string(self.id, "NAME")
    
    def get_name(self):
        if self.is_interior:
            return self.id
        if not self.id:
            return self.region
        return self.id
    
    def get_coords(self):
        return "[{},{}]".format(self.grid_x, self.grid_y)
    
    def record_details(self):
        string = "|Name|    " + str(self) + MwRecord.format_record_details(self, [
        ("\n|Has Water|", "has_water", True if not self.is_interior else False),
        ("\n|Illegal to Sleep Here|", "illegal_to_sleep_here", False),
        ("\n|Behave Like Exterior|", "behave_like_exterior", False),
        ("\n|Water Height|", "water_height", 0 if self.is_interior else None),
        ("\n|Ambient RGB|", "ambient_red"), (", {}", "ambient_green"), (", {}", "ambient_blue"),
        ("\n|Sunlight RGB|", "sunlight_red"), (", {}", "sunlight_green"), (", {}", "sunlight_blue"),
        ("\n|Fog RGB|", "fog_red"), (", {}", "fog_green"), (", {}", "fog_blue"), ("    |Density|", "fog_density"),
        ("\n|Region|", "region", "Wilderness" if self.is_interior else (self.region if self.id == "" else None)),
        ("\n|Map RGB|", "map_red"), (", {}", "map_green"), (", {}", "map_blue")
        ])
        if self.references_loaded:
            for ref in self.references:
                string += "\n" + ref.record_details()
        elif "FRMR" in self.subrecords:
            string += "\nHas References"
        return string
    
    def __str__(self):
        if self.is_interior:
            return self.id
        if not self.id:
            return self.region + " " + self.get_coords()
        return self.id + " " + self.get_coords()
    
    def get_id(self):
        return str(self)
    
    def diff_old(self, other):
        MwRecord.diff(self, other, ["has_water", "illegal_to_sleep_here", "behave_like_exterior", "water_height", "ambient_red", "ambient_green", "ambient_blue", "sunlight_red", "sunlight_green", "sunlight_blue", "fog_red", "fog_green", "fog_blue", "fog_density", "region", "map_red", "map_green", "map_blue"])
        
        ref_details1 = []
        ref_details2 = []
        for ref in self.references:
            ref_details1 += [ref.diff_string()]
        for ref in other.references:
            ref_details2 += [ref.diff_string()]
        
        for ref2 in ref_details2:
            if ref2 not in ref_details1:
                print(str(self) + ": Added", ref2)
        
        for ref1 in ref_details1:
            if ref1 not in ref_details2:
                print(str(self) + ": Removed", ref1)

    def diff(self, other):
        # Like diff_old, but trying to match changed references (for now, only if
        # at a distance of < 200 and with the same ID).
        MwRecord.diff(self, other, ["has_water", "illegal_to_sleep_here", "behave_like_exterior", "water_height", "ambient_red", "ambient_green", "ambient_blue", "sunlight_red", "sunlight_green", "sunlight_blue", "fog_red", "fog_green", "fog_blue", "fog_density", "region", "map_red", "map_green", "map_blue"])

        different = False

        refs1 = defaultdict(list)
        refs2 = defaultdict(list)
        refids = []
        
        for ref in self.references:
            refs1[ref.id].append(ref)
            if ref.id not in refids:
                refids.append(ref.id)
        for ref in other.references:
            refs2[ref.id].append(ref)
            if ref.id not in refids:
                refids.append(ref.id)
        
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
                    print("\n### Cell", str(self) + ": ###")
        
            for ref1 in refs1only:
                # Try to match ref1 with a reference from other that has
                # the same ID and is close by.
                DISTANCE_CUTOFF = 200
                closest_dist = DISTANCE_CUTOFF
                closest_ref = None
                for ref2 in refs2only:
                    dist = ref1.distance(ref2)
                    if dist < closest_dist:
                        closest_ref = ref2
                        closest_dist = dist
                if closest_dist < DISTANCE_CUTOFF:
                    ref1.diff(closest_ref)
                    refs1only.remove(ref1)
                    refs2only.remove(closest_ref)
            
            for ref2 in refs2only:
                print("Added", ref2)
            
            for ref1 in refs1only:
                print("Removed", ref1)

class MwCELLReference:
    diff_list = ["scale", "owner", "global_variable", "faction", "faction_rank", "soul", "charge_left", "uses_left", "door_pos_x", "door_pos_y", "door_pos_z", "door_rot_x", "door_rot_y", "door_rot_z", "door_cell", "lock_level", "key_id", "trap_id", "pos_x", "pos_y", "pos_z", "rot_x", "rot_y", "rot_z"]
    
    def __init__(self):
        self.deleted = False
        self.blocked = False
    
    def get_object_index(self):
        return self.index & 0xFFFFFF
        
    def get_master_index(self):
        return self.index >> 24
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
        ("|ID|", "id"), ("    |Object Index|", "get_object_index"), ("    |Master Index|", "get_master_index"),
        ("\n  |Scale|    {:.2f}", "scale"),
        ("\n  |Owner|", "owner"), ("    |Global Variable|", "global_variable"),
        ("\n  |Faction|", "faction"), ("    |Rank|", "faction_rank"),
        ("\n  |Soul|", "soul"),
        ("\n  |Charge Left|", "charge_left"),
        ("\n  |Uses Left|", "uses_left"),
        ("\n  |Door|    {:.3f}", "door_pos_x"), (", {:.3f}", "door_pos_y"), (", {:.3f}", "door_pos_z"), (" [{:.3f}", "door_rot_x"), (", {:.3f}", "door_rot_y"), (", {:.3f}]", "door_rot_z"), (" {}", "door_cell"),
        ("\n  |Lock|", "lock_level"),
        ("\n  |Key|", "key_id"),
        ("\n  |Trap|", "trap_id"),
        ("\n  |Position|    {:.3f}", "pos_x"), (", {:.3f}", "pos_y"), (", {:.3f}", "pos_z"), (" [{:.3f}", "rot_x"), (", {:.3f}", "rot_y"), (", {:.3f}]", "rot_z")
        ])
    
    def __str__(self):
        return "{} ({:.3f}, {:.3f}, {:.3f})".format(self.id, self.pos_x, self.pos_y, self.pos_z)
    
    def __repr__(self):
        return str(self)
    
    def diff(self, other):
        MwRecord.diff(self, other, MwCELLReference.diff_list)
    
    def diff_string(self):
        return "".join(str(getattr(self, attr, "")) for attr in MwCELLReference.diff_list)

    def distance(self, other):
        # taxicab distance
        return abs(self.pos_x - other.pos_x) + abs(self.pos_y - other.pos_y) + abs(self.pos_z - other.pos_z)