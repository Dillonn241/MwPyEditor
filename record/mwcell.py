import copy
from mwrecord import MwRecord
import mwglobals
from collections import defaultdict

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
        if self.region == None:
            self.region = "Wilderness"
        self.map_red = self.get_subrecord_int("NAM5", start=0, length=1, signed=False)
        self.map_green = self.get_subrecord_int("NAM5", start=1, length=1, signed=False)
        self.map_blue = self.get_subrecord_int("NAM5", start=2, length=1, signed=False)
        
        if self.is_interior:
            if self.id not in mwglobals.interior_cells:
                mwglobals.interior_cells[self.id] = self
        else:
            grid = (self.grid_x, self.grid_y)
            if grid not in mwglobals.exterior_cells:
                mwglobals.exterior_cells[grid] = self
        
        if init_references:
            self.load_references()
    
    def load_references(self):
        self.references = {}
        reference = None
        for subrecord in self.ordered_subrecords:
            if subrecord.record_type == "FRMR":
                reference = MwCELLReference()
                reference.index = subrecord.get_int()
                self.references[reference.index] = reference
            elif reference != None:
                if subrecord.record_type == "NAME":
                    reference.id = subrecord.get_string()
                elif subrecord.record_type == "XSCL":
                    reference.scale = subrecord.get_float()
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
                elif subrecord.record_type == "ANAM":
                    reference.owner = subrecord.get_string()
                elif subrecord.record_type == "BNAM":
                    reference.global_variable_rank = subrecord.get_string()
                elif subrecord.record_type == "XCHG":
                    reference.charge_left = subrecord.get_float()
                elif subrecord.record_type == "INTV":
                    reference.uses_left = subrecord.get_int()
                elif subrecord.record_type == "XSOL":
                    reference.soul = subrecord.get_string()
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
                old_refs = mwglobals.interior_cells[self.id].references
                mwglobals.interior_cells[self.id] = copy.copy(self)
                mwglobals.interior_cells[self.id].references = copy.copy(self.references)
                mwglobals.interior_cells[self.id].references.update(old_refs)
        else:
            grid = (self.grid_x, self.grid_y)
            if grid in mwglobals.exterior_cells:
                old_refs = mwglobals.exterior_cells[grid].references
                mwglobals.exterior_cells[grid] = copy.copy(self)
                mwglobals.exterior_cells[grid].references = copy.copy(self.references)
                mwglobals.exterior_cells[grid].references.update(old_refs)
        
        self.references_loaded = True
    
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
            for ref in self.references.values():
                string += "\n\n" + ref.record_details()
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
    
    def compare_old(self, other):
        MwRecord.compare(self, other, ["has_water", "illegal_to_sleep_here", "behave_like_exterior", "water_height", "ambient_red", "ambient_green", "ambient_blue", "sunlight_red", "sunlight_green", "sunlight_blue", "fog_red", "fog_green", "fog_blue", "fog_density", "region", "map_red", "map_green", "map_blue"])
        
        ref_details1 = []
        ref_details2 = []
        for ref in self.references.values():
            ref_details1 += [ref.record_details()]
        for ref in other.references.values():
            ref_details2 += [ref.record_details()]
        
        for ref2 in ref_details2:
            if ref2 not in ref_details1:
                print(str(self) + " Added " + str(ref2))
        
        for ref1 in ref_details1:
            if ref1 not in ref_details2:
                print(str(self) + " Removed " + str(ref1))

    def compare(self, other):
        # Like compare, but trying to match changed references (for now, only if
        # at a distance of < 200 and with the same ID).
        MwRecord.compare(self, other, ["has_water", "illegal_to_sleep_here", "behave_like_exterior", "water_height", "ambient_red", "ambient_green", "ambient_blue", "sunlight_red", "sunlight_green", "sunlight_blue", "fog_red", "fog_green", "fog_blue", "fog_density", "region", "map_red", "map_green", "map_blue"])

        different = False

        refs1 = defaultdict(list)
        refs2 = defaultdict(list)
        refids = []
        
        for ref in self.references.values():
            refs1[ref.id].append(ref)
            if ref.id not in refids:
                refids.append(ref.id)
        for ref in other.references.values():
            refs2[ref.id].append(ref)
            if ref.id not in refids:
                refids.append(ref.id)
        
        for refid in refids:
            # Form the set differences between refs1[refid] and refs2[refid]:
            refs1_refid_strings = [str(ref1.record_details()) for ref1 in refs1[refid]]
            refs2_refid_strings = [str(ref2.record_details()) for ref2 in refs2[refid]]
            refs1only = [ref1 for ref1 in refs1[refid] if
                         str(ref1.record_details()) not in refs2_refid_strings]
            refs2only = [ref2 for ref2 in refs2[refid] if
                         str(ref2.record_details()) not in refs1_refid_strings]
        
            if not different:
                if refs1only or refs2only:
                    different = True
                    print("### Cell " + str(self.get_id()) + ": ###")
        
            for ref1 in refs1only:
                # Try to match ref1 with a reference from other that has
                # the same ID and is close by.
                dist = 1000000
                closest_ref = None
                for ref2 in refs2only:
                    if ref1.distance(ref2) < dist:
                        closest_ref = ref2
                        dist = ref1.distance(ref2)
                if dist < 200:
                    print("Cell " + str(self) + ": Changed\n " + str(ref1.record_details())
                          + "\n to\n " + str(ref2.record_details()))
                    refs1only.remove(ref1)
                    refs2only.remove(closest_ref)
            
            for ref2 in refs2only:
                print("Cell " + str(self) + ": Added " + str(ref2.record_details()))
            
            for ref1 in refs1only:
                print("Cell " + str(self) + ": Removed " + str(ref1.record_details()))

class MwCELLReference:
    def __init__(self):
        self.deleted = False
    
    def record_details(self):
        return MwRecord.format_record_details(self, [
        ("|ID|", "id"),
        ("\n|Position|    {:.3f}", "pos_x"), (", {:.3f}", "pos_y"), (", {:.3f}", "pos_z"), (" [{:.3f}", "rot_x"), (", {:.3f}", "rot_y"), (", {:.3f}]", "rot_z"),
        ("\n|Scale|", "scale"),
        ("\n|Door|    {:.3f}", "door_pos_x"), (", {:.3f}", "door_pos_y"), (", {:.3f}", "door_pos_z"), (" [{:.3f}", "door_rot_x"), (", {:.3f}", "door_rot_y"), (", {:.3f}]", "door_rot_z"), (" {}", "door_cell"),
        ("\n|Lock|", "lock_level"), ("    |Key|", "key_id"), ("    |Trap|", "trap_id"),
        ("\n|Owner|", "owner"), ("    |Global Variable/Rank|", "global_variable_rank"),
        ("\n|Charge Left|", "charge_left"), ("    |Uses Left|", "uses_left"), ("    |Soul|", "soul")
        ])
    
    def __str__(self):
        return self.id
    
    def __repr__(self):
        return str(self)
    
    def compare(self, other):
        MwRecord.compare(self, other, ["id", "pos_x", "pos_y", "pos_z", "rot_x", "rot_y", "rot_z", "scale", "door_pos_x", "door_pos_y", "door_pos_z", "door_rot_x", "door_rot_y", "door_rot_z", "door_cell", "lock_level", "key_id", "trap_id", "owner", "global_variable_rank", "charge_left", "uses_left", "soul"])

    def distance(self, other):
        # taxicab distance
        return abs(self.pos_x - other.pos_x) + abs(self.pos_y - other.pos_y) + abs(self.pos_z - other.pos_z)