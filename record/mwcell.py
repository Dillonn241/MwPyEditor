from collections import defaultdict
import copy

import mwglobals
from mwrecord import MwRecord
import record.mwligh as mwligh

init_references = False


class MwCELL(MwRecord):
    def __init__(self):
        MwRecord.__init__(self)
        self.references = []
    
    def load(self):
        self.id = self.get_subrecord_string("NAME")
        
        flags = self.get_subrecord_uint("DATA", start=0, length=4)
        self.is_interior = (flags & 0x1) == 0x1
        self.has_water = (flags & 0x2) == 0x2
        self.illegal_to_sleep_here = (flags & 0x4) == 0x4
        self.named_exterior = (flags & 0x40) == 0x40
        self.behave_like_exterior = (flags & 0x80) == 0x80
        self.grid_x = self.get_subrecord_int("DATA", start=4, length=4)
        self.grid_y = self.get_subrecord_int("DATA", start=8, length=4)
        
        self.region = self.get_subrecord_string("RGNN")
        self.map_red = self.get_subrecord_uint("NAM5", start=0, length=1)
        self.map_green = self.get_subrecord_uint("NAM5", start=1, length=1)
        self.map_blue = self.get_subrecord_uint("NAM5", start=2, length=1)
        
        self.water_height = self.get_subrecord_float("WHGT")
        self.ambient_red = self.get_subrecord_uint("AMBI", start=0, length=1)
        self.ambient_green = self.get_subrecord_uint("AMBI", start=1, length=1)
        self.ambient_blue = self.get_subrecord_uint("AMBI", start=2, length=1)
        self.sunlight_red = self.get_subrecord_uint("AMBI", start=4, length=1)
        self.sunlight_green = self.get_subrecord_uint("AMBI", start=5, length=1)
        self.sunlight_blue = self.get_subrecord_uint("AMBI", start=6, length=1)
        self.fog_red = self.get_subrecord_uint("AMBI", start=8, length=1)
        self.fog_green = self.get_subrecord_uint("AMBI", start=9, length=1)
        self.fog_blue = self.get_subrecord_uint("AMBI", start=10, length=1)
        self.fog_density = self.get_subrecord_float("AMBI", start=12, length=4)

        self.nam0 = self.get_subrecord_uint("NAM0")
        
        if init_references:
            self.load_references()
        
        if self.is_interior:
            if self.id not in mwglobals.interior_cells:
                mwglobals.interior_cells[self.id] = copy.copy(self)
                mwglobals.interior_cells[self.id].references = copy.copy(self.references)
        else:
            grid = (self.grid_x, self.grid_y)
            if grid not in mwglobals.exterior_cells:
                mwglobals.exterior_cells[grid] = copy.copy(self)
                mwglobals.exterior_cells[grid].references = copy.copy(self.references)
    
    def load_references(self):
        ref = None
        for subrecord in self.ordered_subrecords:
            if subrecord.record_type == "MVRF":
                ref = MwCELLReference()
                ref.index = subrecord.get_uint()
                ref.moved = False
                self.references += [ref]
            elif subrecord.record_type == "FRMR":
                if ref is not None and not getattr(ref, "moved", True):
                    ref.moved = True
                else:
                    ref = MwCELLReference()
                    ref.index = subrecord.get_uint()
                    self.references += [ref]
            elif ref is not None:
                if subrecord.record_type == "CNDT":
                    ref.moved_grid_x = subrecord.get_int(start=0, length=4)
                    ref.moved_grid_y = subrecord.get_int(start=4, length=4)
                elif subrecord.record_type == "NAME":
                    ref.id = subrecord.get_string()
                elif subrecord.record_type == "UNAM":
                    ref.blocked = True
                elif subrecord.record_type == "XSCL":
                    ref.scale = subrecord.get_float()
                elif subrecord.record_type == "ANAM":
                    ref.owner = subrecord.get_string()
                elif subrecord.record_type == "BNAM":
                    ref.global_variable = subrecord.get_string()
                elif subrecord.record_type == "CNAM":
                    if hasattr(ref, "moved") and not ref.moved:
                        ref.moved_cell = subrecord.get_string()
                    else:
                        ref.faction = subrecord.get_string()
                elif subrecord.record_type == "INDX":
                    ref.faction_rank = subrecord.get_uint()
                elif subrecord.record_type == "XSOL":
                    ref.soul = subrecord.get_string()
                elif subrecord.record_type == "XCHG":
                    ref.charge_left = subrecord.get_float()
                elif subrecord.record_type == "INTV":
                    if ref.id in mwglobals.object_ids and isinstance(mwglobals.object_ids[ref.id], mwligh.MwLIGH):
                        ref.uses_left = subrecord.get_float()
                    else:
                        ref.uses_left = subrecord.get_uint()
                elif subrecord.record_type == "NAM9":
                    ref.stack_size = subrecord.get_uint()
                elif subrecord.record_type == "DODT":
                    ref.door_pos_x = subrecord.get_float(start=0, length=4)
                    ref.door_pos_y = subrecord.get_float(start=4, length=4)
                    ref.door_pos_z = subrecord.get_float(start=8, length=4)
                    ref.door_rot_x = subrecord.get_float(start=12, length=4)
                    ref.door_rot_y = subrecord.get_float(start=16, length=4)
                    ref.door_rot_z = subrecord.get_float(start=20, length=4)
                elif subrecord.record_type == "DNAM":
                    ref.door_cell = subrecord.get_string()
                elif subrecord.record_type == "FLTV":
                    ref.lock_level = subrecord.get_uint()
                elif subrecord.record_type == "KNAM":
                    ref.key_id = subrecord.get_string()
                elif subrecord.record_type == "TNAM":
                    ref.trap_id = subrecord.get_string()
                elif subrecord.record_type == "DATA":
                    ref.pos_x = subrecord.get_float(start=0, length=4)
                    ref.pos_y = subrecord.get_float(start=4, length=4)
                    ref.pos_z = subrecord.get_float(start=8, length=4)
                    ref.rot_x = subrecord.get_float(start=12, length=4)
                    ref.rot_y = subrecord.get_float(start=16, length=4)
                    ref.rot_z = subrecord.get_float(start=20, length=4)
                elif subrecord.record_type == "DELE":
                    ref.deleted = True
        
        if self.is_interior:
            if self.id in mwglobals.interior_cells:
                self.update_references(mwglobals.interior_cells, self.id)
        else:
            grid = (self.grid_x, self.grid_y)
            if grid in mwglobals.exterior_cells:
                self.update_references(mwglobals.exterior_cells, grid)
    
    def update_references(self, cell_list, cell_index):
        cell_copy = copy.copy(self)
        cell_copy.references = copy.copy(cell_list[cell_index].references)
        for ref in self.references:
            if ref.get_master_index() == 0:
                cell_copy.references += [ref]
            else:
                cell_copy.references = [ref if x.get_object_index() == ref.get_object_index() else x for x in cell_copy.references]
        cell_list[cell_index] = cell_copy
    
    def save(self):
        self.clear_subrecords()
        self.add_subrecord_string(self.id, "NAME")
        sub_data = self.add_subrecord("DATA")
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
        
        self.add_subrecord_string(self.region, "RGNN")
        if self.map_red is not None:
            sub_nam5 = self.add_subrecord("NAM5")
            sub_nam5.add_uint(self.map_red, length=1)
            sub_nam5.add_uint(self.map_green, length=1)
            sub_nam5.add_uint(self.map_blue, length=1)
            sub_nam5.add_uint(0, length=1)
        
        self.add_subrecord_float(self.water_height, "WHGT")
        if self.ambient_red is not None:
            sub_ambi = self.add_subrecord("AMBI")
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
        
        def save_reference(self, ref):
            self.add_subrecord_uint(ref.index, "FRMR")
            self.add_subrecord_string(ref.id, "NAME")
            if ref.is_blocked():
                self.add_subrecord_uint(0, "UNAM", length=1)
            if hasattr(ref, "scale"):
                self.add_subrecord_float(ref.scale, "XSCL")
            if hasattr(ref, "owner"):
                self.add_subrecord_string(ref.owner, "ANAM")
            if hasattr(ref, "global_variable"):
                self.add_subrecord_string(ref.global_variable, "BNAM")
            if hasattr(ref, "faction"):
                self.add_subrecord_string(ref.faction, "CNAM")
            if hasattr(ref, "faction_rank"):
                self.add_subrecord_uint(ref.faction_rank, "INDX")
            if hasattr(ref, "soul"):
                self.add_subrecord_string(ref.soul, "XSOL")
            if hasattr(ref, "charge_left"):
                self.add_subrecord_float(ref.charge_left, "XCHG")
            if hasattr(ref, "uses_left"):
                if isinstance(mwglobals.object_ids[ref.id], mwligh.MwLIGH):
                    self.add_subrecord_float(ref.uses_left, "INTV")
                else:
                    self.add_subrecord_uint(ref.uses_left, "INTV")
            if hasattr(ref, "stack_size"):
                self.add_subrecord_uint(ref.stack_size, "NAM9")
            if hasattr(ref, "door_pos_x"):
                sub_dodt = self.add_subrecord("DODT")
                sub_dodt.add_float(ref.door_pos_x)
                sub_dodt.add_float(ref.door_pos_y)
                sub_dodt.add_float(ref.door_pos_z)
                sub_dodt.add_float(ref.door_rot_x)
                sub_dodt.add_float(ref.door_rot_y)
                sub_dodt.add_float(ref.door_rot_z)
            if hasattr(ref, "door_cell"):
                self.add_subrecord_string(ref.door_cell, "DNAM")
            if hasattr(ref, "lock_level"):
                self.add_subrecord_uint(ref.lock_level, "FLTV")
            if hasattr(ref, "key_id"):
                self.add_subrecord_string(ref.key_id, "KNAM")
            if hasattr(ref, "trap_id"):
                self.add_subrecord_string(ref.trap_id, "TNAM")
            if hasattr(ref, "pos_x"):
                sub_dodt = self.add_subrecord("DATA")
                sub_dodt.add_float(ref.pos_x)
                sub_dodt.add_float(ref.pos_y)
                sub_dodt.add_float(ref.pos_z)
                sub_dodt.add_float(ref.rot_x)
                sub_dodt.add_float(ref.rot_y)
                sub_dodt.add_float(ref.rot_z)
            if ref.is_deleted():
                self.add_subrecord_int(0, "DELE")

        self.references.sort(key=lambda x: (not x.is_persistent_child, x.get_master_index(), x.get_object_index()))
        num_refs = len(self.references)
        nam0 = -1
        for i in range(num_refs):
            ref = self.references[i]
            if ref.is_moved():
                self.add_subrecord_uint(ref.index, "MVRF")
                if hasattr(ref, "moved_cell"):
                    self.add_subrecord_string(ref.moved_cell, "CNAM")
                if hasattr(ref, "moved_grid_x"):
                    sub_cndt = self.add_subrecord("CNDT")
                    sub_cndt.add_int(ref.moved_grid_x)
                    sub_cndt.add_int(ref.moved_grid_y)
            elif nam0 == -1 and not ref.is_persistent_child():
                nam0 = num_refs - i
                self.add_subrecord_uint(nam0, "NAM0")
            save_reference(self, ref)
    
    def get_region(self):
        if not self.is_interior and self.region is None:
            return "Wilderness"
        return self.region
    
    def get_name(self):
        if self.is_interior or self.id:
            return self.id
        return self.region
    
    def get_coords(self):
        return "[{},{}]".format(self.grid_x, self.grid_y)
    
    def record_details(self):
        string = "|Name|    " + str(self) + MwRecord.format_record_details(self, [
            ("\n|Has Water|", "has_water", True if not self.is_interior else False),
            ("\n|Illegal to Sleep Here|", "illegal_to_sleep_here", False),
            ("\n|Behave Like Exterior|", "behave_like_exterior", False),
            ("\n|Region|", "region"),
            ("\n|Map RGB|", "map_red"), (", {}", "map_green"), (", {}", "map_blue"),
            ("\n|Water Height|", "water_height", 0 if self.is_interior else None),
            ("\n|Ambient RGB|", "ambient_red"), (", {}", "ambient_green"), (", {}", "ambient_blue"),
            ("\n|Sunlight RGB|", "sunlight_red"), (", {}", "sunlight_green"), (", {}", "sunlight_blue"),
            ("\n|Fog RGB|", "fog_red"), (", {}", "fog_green"), (", {}", "fog_blue"), ("    |Density|", "fog_density")
        ])
        if init_references:
            for ref in self.references:
                string += "\n" + ref.record_details()
        elif "FRMR" in self.subrecords:
            string += "\nHas References"
        return string
    
    def __str__(self):
        if self.is_interior:
            return self.id
        if self.id:
            return self.id + " " + self.get_coords()
        return self.region + " " + self.get_coords()
    
    def get_id(self):
        return str(self)
    
    def diff_old(self, other):
        MwRecord.diff(self, other, ["has_water", "illegal_to_sleep_here", "behave_like_exterior", "region", "map_red",
                                    "map_green", "map_blue", "water_height", "ambient_red", "ambient_green",
                                    "ambient_blue", "sunlight_red", "sunlight_green", "sunlight_blue", "fog_red",
                                    "fog_green", "fog_blue", "fog_density"])
        
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
        MwRecord.diff(self, other, ["has_water", "illegal_to_sleep_here", "behave_like_exterior", "region", "map_red",
                                    "map_green", "map_blue", "water_height", "ambient_red", "ambient_green",
                                    "ambient_blue", "sunlight_red", "sunlight_green", "sunlight_blue", "fog_red",
                                    "fog_green", "fog_blue", "fog_density"])

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
                    print("### Cell", str(self) + ": ###\n")
        
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
    diff_list = ["scale", "owner", "global_variable", "faction", "faction_rank", "soul", "charge_left", "uses_left",
                 "door_pos_x", "door_pos_y", "door_pos_z", "door_rot_x", "door_rot_y", "door_rot_z", "door_cell",
                 "lock_level", "key_id", "trap_id", "pos_x", "pos_y", "pos_z", "rot_x", "rot_y", "rot_z"]
    
    def is_persistent_child(self):
        if hasattr(self, "door_cell") or hasattr(self, "door_pos_x"):
            return True
        obj = mwglobals.object_ids[self.id]
        if obj.persists:
            return True
        obj_record_type = obj.get_record_type()
        if obj_record_type == "CREA" or obj_record_type == "NPC_":
            return True
        return False
    
    def get_object_index(self):
        return self.index & 0xFFFFFF
        
    def get_master_index(self):
        return self.index >> 24
    
    def is_moved(self):
        return hasattr(self, "moved")
    
    def is_blocked(self):
        return hasattr(self, "blocked")
    
    def is_deleted(self):
        return hasattr(self, "deleted")
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
            ("|ID|", "id"), ("    |Object Index|", "get_object_index"), ("    |Master Index|", "get_master_index"),
            ("\n  |Scale|    {:.2f}", "scale"),
            ("\n  |Owner|", "owner"), ("    |Global Variable|", "global_variable"),
            ("\n  |Faction|", "faction"), ("    |Rank|", "faction_rank"),
            ("\n  |Soul|", "soul"),
            ("\n  |Charge Left|", "charge_left"),
            ("\n  |Uses Left|", "uses_left"),
            ("\n  |Door|    {:.3f}", "door_pos_x"), (", {:.3f}", "door_pos_y"), (", {:.3f}", "door_pos_z"),
            (" [{:.3f}", "door_rot_x"), (", {:.3f}", "door_rot_y"), (", {:.3f}]", "door_rot_z"), (" {}", "door_cell"),
            ("\n  |Lock|", "lock_level"),
            ("\n  |Key|", "key_id"),
            ("\n  |Trap|", "trap_id"),
            ("\n  |Position|    {:.3f}", "pos_x"), (", {:.3f}", "pos_y"), (", {:.3f}", "pos_z"), (" [{:.3f}", "rot_x"),
            (", {:.3f}", "rot_y"), (", {:.3f}]", "rot_z")
        ])
    
    def __str__(self):
        if hasattr(self, "pos_x"):
            return "{} ({:.3f}, {:.3f}, {:.3f})".format(self.id, self.pos_x, self.pos_y, self.pos_z)
        return self.id
    
    def __repr__(self):
        return str(self)
    
    def diff(self, other):
        MwRecord.diff(self, other, MwCELLReference.diff_list)
    
    def diff_string(self):
        return "".join(str(getattr(self, attr, "")) for attr in MwCELLReference.diff_list)

    def distance(self, other):
        # taxicab distance
        return abs(self.pos_x - other.pos_x) + abs(self.pos_y - other.pos_y) + abs(self.pos_z - other.pos_z)
