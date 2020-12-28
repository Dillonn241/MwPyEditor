import sys
import struct
import time
import argparse
import record.mwtes3 as mwtes3
import record.mwgmst as mwgmst
import record.mwglob as mwglob
import record.mwclas as mwclas
import record.mwfact as mwfact
import record.mwrace as mwrace
import record.mwsoun as mwsoun
import record.mwskil as mwskil
import record.mwmgef as mwmgef
import record.mwscpt as mwscpt
import record.mwregn as mwregn
import record.mwbsgn as mwbsgn
import record.mwltex as mwltex
import record.mwstat as mwstat
import record.mwdoor as mwdoor
import record.mwmisc as mwmisc
import record.mwweap as mwweap
import record.mwcont as mwcont
import record.mwspel as mwspel
import record.mwcrea as mwcrea
import record.mwbody as mwbody
import record.mwligh as mwligh
import record.mwench as mwench
import record.mwnpc_ as mwnpc_
import record.mwarmo as mwarmo
import record.mwclot as mwclot
import record.mwrepa as mwrepa
import record.mwacti as mwacti
import record.mwappa as mwappa
import record.mwlock as mwlock
import record.mwprob as mwprob
import record.mwingr as mwingr
import record.mwbook as mwbook
import record.mwalch as mwalch
import record.mwlevi as mwlevi
import record.mwlevc as mwlevc
import record.mwcell as mwcell
import record.mwland as mwland
import record.mwpgrd as mwpgrd
import record.mwsndg as mwsndg
import record.mwdial as mwdial
import record.mwinfo as mwinfo
import record.mwsscr as mwsscr
import mwglobals
import mwjobs

plugin_records = {}

def init():
    """Choose at most one: list of records loaded by default for every plugin. TES3 should always be loaded."""
    mwglobals.default_records = mwglobals.RECORDS_MIN # minimum types required for autocalc: MGEF, CLAS, RACE, SKIL
    #mwglobals.default_records = mwglobals.RECORDS_MOST # all types except: DIAL, INFO, CELL, LAND
    #mwglobals.default_records = mwglobals.RECORDS_ALL # all types
    
    """Expand list of records loaded by default for every plugin."""
    mwglobals.default_records += []
    
    """Choose any: load large data for CELL and LAND."""
    mwcell.init_references = True # statics and other references placed in the world
    #mwland.init_lod = True # lod to show global map
    #mwland.init_terrain = True # normals, heights, colors, and textures of landscape (long load time)
    
    """Choose any: run algorithms to autocalc stats for ALCH, ENCH, SPEL, and NPC_."""
    #mwalch.do_autocalc = True # requires MGEF
    #mwench.do_autocalc = True # requires MGEF
    #mwspel.do_autocalc = True # requires MGEF
    #mwnpc_.do_autocalc = True # requires CLAS, RACE, SKIL
    
    """Load any plugins you want. Masters are automatically loaded."""
    # Vanilla
    #load_plugin("Morrowind.esm")
    #load_plugin("Tribunal.esm")
    #load_plugin("Bloodmoon.esm")
    
    # DLC
    #load_plugin("adamantiumarmor.esp")
    #load_plugin("AreaEffectArrows.esp")
    #load_plugin("bcsounds.esp")
    #load_plugin("EBQ_Artifact.esp")
    #load_plugin("entertainers.esp")
    #load_plugin("LeFemmArmor.esp")
    #load_plugin("master_index.esp")
    #load_plugin("Siege at Firemoth.esp")
    
    # Tamriel Data
    #load_plugin("Tamriel_Data_6.esm")
    #load_plugin("Tamriel_Data_7.esm")
    #load_plugin("Tamriel_Data_7.1.esm")
    #load_plugin("Tamriel_Data.esm")
    
    # Released versions of province mods
    #load_plugin("Unused/TR_Mainland_1809.esm")
    #load_plugin("Unused/TR_Mainland_1912.esm")
    #load_plugin("Unused/TR_Mainland_2002.esm")
    #load_plugin("Unused/Cyrodiil_Main_0.2.esm")
    #load_plugin("Unused/Sky_Main_02.esp")
    #load_plugin("Unused/Sky_Main_1812.esm")
    #load_plugin("Unused/Sky_Main_1903.esm")
    #load_plugin("Unused/Sky_Main_2001.esm")
    
    # Tamriel Rebuilt
    #load_plugin("TR_Mainland.esp")
    #load_plugin("TR_Factions.esp")
    #load_plugin("TR_Travels.esp")
    #load_plugin("TR_Travels_(Preview_and_Mainland).esp")
    #load_plugin("TR_Andothren_v.0050.esp")
    #load_plugin("TR_RorynsBluff_v0209.esp")
    #load_plugin("TR_ArmunAshlands_v0040.esp")
    #load_plugin("TR_SouthernVelothis_v.0009.esp")
    #load_plugin("TR_ThirrValley_v0070.ESP")
    #load_plugin("TR_Kartur_v0021.esp")
    #load_plugin("TR_RestExterior.esp")
    
    # Skyrim: Home of the Nords
    #load_plugin("Sky_Main_2020_12_26b.esp")
    #load_plugin("Sky_Markarth_2020-12-21.ESP")
    #load_plugin("Sky_Falkheim_2020-10-10.ESP")
    
    # Province: Cyrodiil
    #load_plugin("Cyrodiil_Main_2020_12_23.ESP")
    #load_plugin("PC_Anvil_v0058.ESP")
    #load_plugin("PC_Sutch_v0015.ESP")
    
    print()

def handle_args(args):
    if args.command:
        if args.command == "diff":
            args_diff(args)
        elif args.command == "dump":
            args_dump(args)

def args_diff(args):
    if len(args.plugins) != 2:
        sys.exit("Exactly two plugins can be compared!")
    plugin1 = args.plugins[0] # "Tamriel_Data_6.esm"
    plugin2 = args.plugins[1] # "Tamriel_Data.esm"
    record_types = args.type if args.type else mwglobals.RECORDS_ALL
    load_plugin(plugin1, records_to_load=record_types)
    load_plugin(plugin2, records_to_load=record_types)
    print()
    print("# Diff plugin " + str(plugin1) + " with " + str(plugin2) + ": #")
    
    diff_added = args.diff_added if args.diff_added else False
    diff_removed = args.diff_removed if args.diff_removed else False
    diff_changed = not args.diff_ignore_changed if args.diff_ignore_changed else True
    for rcd_type in record_types:
        print()
        print("## Diff record type " + str(rcd_type) + ": ##")
        diff_plugins(plugin1, plugin2, rcd_type, added=diff_added, removed=diff_removed, changed=diff_changed)
    print()

def args_dump(args):
    for plugin in args.plugins:
        record_types = args.type if args.type else mwglobals.RECORDS_ALL
        load_plugin(plugin, records_to_load=record_types)
        print()
        print("# Dump plugin " + plugin + ": #")
        for rcd_type in record_types:
            print()
            print("## Dump record type " + rcd_type + ": ##")
            if args.list:
                print()
                for rcd in plugin_records[plugin][rcd_type]:
                    print(rcd)
            else:
                for rcd in plugin_records[plugin][rcd_type]:
                    print()
                    print(rcd.record_details())
        print()

def load_plugin(file_name, records_to_load=None):
    # use default_records if no argument is provided for records_to_load
    if records_to_load is None:
        records_to_load = mwglobals.default_records
    # DIAL should always be loaded if INFO is
    if "INFO" in records_to_load and "DIAL" not in records_to_load:
        records_to_load = records_to_load + ["DIAL"]
    if file_name in plugin_records:
        # if the plugin has already been loaded before, only load what is still unloaded
        records_to_load = [x for x in records_to_load if x not in plugin_records[file_name]]
    else:
        # if this is the first time, set up the plugin_records data structure
        plugin_records[file_name] = {}
        for rcd_type in records_to_load:
            plugin_records[file_name][rcd_type] = []
    # nothing to do if records_to_load is empty
    if not records_to_load:
        return
    # read the plugin file
    with open(mwglobals.DATA_PATH + file_name, mode='rb') as file:
        while True:
            header = file.read(16)
            if header == b'':
                break
            record_type, length, unknown, flags = struct.unpack("<4siii", header)
            record_type = record_type.decode("mbcs")
            length_left = length
            if record_type not in records_to_load:
                file.seek(length_left, 1)
                continue
            record = create_record(record_type)
            record.file_name = file_name
            mwglobals.records[record_type] += [record]
            mwglobals.ordered_records += [record]
            plugin_records[file_name][record_type] += [record]
            
            while length_left > 0:
                subtype, sublength = struct.unpack("<4si", file.read(8))
                subtype = subtype.decode("mbcs")
                record.add_subrecord(subtype, file.read(sublength))
                length_left -= 8 + sublength
            
            record.load_universal(flags)
            record.load()
            if record_type == "TES3":
                for master in record.masters:
                    load_plugin(master)
                print("** Loading " + file_name + ": " + str(records_to_load) + " **")

def save_plugin(file_name, other_files=[]):
    print(file_name)
    files = other_files + [file_name]
    with open(file_name, mode='wb') as file:
        for record in mwglobals.ordered_records:
            if record.file_name in files:
                if hasattr(record, "save"): # temporary until all are implemented
                    record.save()
                flags = record.save_universal()
                length = 0
                for subrecord in record.ordered_subrecords:
                    length += 8 + len(subrecord.data)
                file.write(struct.pack("<4siii", record.get_record_type().encode("mbcs"), length, 0, flags))
                for subrecord in record.ordered_subrecords:
                    file.write(struct.pack("<4si", subrecord.record_type.encode("mbcs"), len(subrecord.data)))
                    file.write(subrecord.data)

def create_record(record_type):
    if record_type == "TES3":
        return mwtes3.MwTES3()
    elif record_type == "GMST":
        return mwgmst.MwGMST()
    elif record_type == "GLOB":
        return mwglob.MwGLOB()
    elif record_type == "CLAS":
        return mwclas.MwCLAS()
    elif record_type == "FACT":
        return mwfact.MwFACT()
    elif record_type == "RACE":
        return mwrace.MwRACE()
    elif record_type == "SOUN":
        return mwsoun.MwSOUN()
    elif record_type == "SKIL":
        return mwskil.MwSKIL()
    elif record_type == "MGEF":
        return mwmgef.MwMGEF()
    elif record_type == "SCPT":
        return mwscpt.MwSCPT()
    elif record_type == "REGN":
        return mwregn.MwREGN()
    elif record_type == "BSGN":
        return mwbsgn.MwBSGN()
    elif record_type == "LTEX":
        return mwltex.MwLTEX()
    elif record_type == "STAT":
        return mwstat.MwSTAT()
    elif record_type == "DOOR":
        return mwdoor.MwDOOR()
    elif record_type == "MISC":
        return mwmisc.MwMISC()
    elif record_type == "WEAP":
        return mwweap.MwWEAP()
    elif record_type == "CONT":
        return mwcont.MwCONT()
    elif record_type == "SPEL":
        return mwspel.MwSPEL()
    elif record_type == "CREA":
        return mwcrea.MwCREA()
    elif record_type == "BODY":
        return mwbody.MwBODY()
    elif record_type == "LIGH":
        return mwligh.MwLIGH()
    elif record_type == "ENCH":
        return mwench.MwENCH()
    elif record_type == "NPC_":
        return mwnpc_.MwNPC_()
    elif record_type == "ARMO":
        return mwarmo.MwARMO()
    elif record_type == "CLOT":
        return mwclot.MwCLOT()
    elif record_type == "REPA":
        return mwrepa.MwREPA()
    elif record_type == "ACTI":
        return mwacti.MwACTI()
    elif record_type == "APPA":
        return mwappa.MwAPPA()
    elif record_type == "LOCK":
        return mwlock.MwLOCK()
    elif record_type == "PROB":
        return mwprob.MwPROB()
    elif record_type == "INGR":
        return mwingr.MwINGR()
    elif record_type == "BOOK":
        return mwbook.MwBOOK()
    elif record_type == "ALCH":
        return mwalch.MwALCH()
    elif record_type == "LEVI":
        return mwlevi.MwLEVI()
    elif record_type == "LEVC":
        return mwlevc.MwLEVC()
    elif record_type == "CELL":
        return mwcell.MwCELL()
    elif record_type == "LAND":
        return mwland.MwLAND()
    elif record_type == "PGRD":
        return mwpgrd.MwPGRD()
    elif record_type == "SNDG":
        return mwsndg.MwSNDG()
    elif record_type == "DIAL":
        return mwdial.MwDIAL()
    elif record_type == "INFO":
        info = mwinfo.MwINFO()
        last_dial = mwglobals.records["DIAL"][-1]
        last_dial.infos += [info]
        info.dial = last_dial
        return info
    elif record_type == "SSCR":
        return mwsscr.MwSSCR()

def diff_plugins(plugin1, plugin2, record_type, added=True, removed=True, changed=True):
    object_ids1 = {}
    object_ids2 = {}
    for record in mwglobals.records[record_type]:
        if record.file_name == plugin1:
            object_ids1[record.get_id()] = record
        elif record.file_name == plugin2:
            object_ids2[record.get_id()] = record
    
    if added:
        for record in mwglobals.records[record_type]:
            if record.file_name == plugin2:
                if record.get_id() not in object_ids1:
                    print()
                    print("Added " + str(record))
                    print(record.record_details())
    
    if removed:
        for record in mwglobals.records[record_type]:
            if record.file_name == plugin1:
                if record.get_id() not in object_ids2:
                    print()
                    print("Removed " + str(record))
    
    if changed:
        for record in mwglobals.records[record_type]:
            if record.file_name == plugin1:
                if record.get_id() in object_ids2:
                    record2 = object_ids2[record.get_id()]
                    record.diff(record2)

def diff_locations(plugin1, file_names1, plugin2, file_names2, record_type):
    file_names1 += [plugin1]
    file_names2 += [plugin2]
    object_ids2 = {}
    for record in mwglobals.records[record_type]:
        if record.file_name == plugin2:
            object_ids2[record.get_id()] = record
    
    for record in mwglobals.records[record_type]:
        if record.file_name == plugin1:
            if record.get_id() in object_ids2:
                first_print = True
                record2 = object_ids2[record.get_id()]
                locations1 = mwjobs.find_item_usage(record.get_id(), file_names=file_names1)
                locations2 = mwjobs.find_item_usage(record2.get_id(), file_names=file_names2)
                for loc in locations1:
                    if loc not in locations2:
                        if first_print:
                            print(record)
                            first_print = False
                        print("- " + loc)
                for loc in locations2:
                    if loc not in locations1:
                        if first_print:
                            print(record)
                            first_print = False
                        print("+ " + loc)

def main(args):
    start = time.time()
    init()
    handle_args(args)
    end = time.time()
    print()
    print("** Time spent: {:.3f} seconds **".format(end - start))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description="Analyze a plugin file."
    "\n\nThe following commands are available:"
    "\ndiff\tfind the difference between two plugins"
    "\ndump\toutput readable record data")
    parser.add_argument("command", help="name of the action to take")
    parser.add_argument("plugins", help="list of plugins to load and provide as arguments", nargs="+")
    parser.add_argument("-l", "--list", help="show only identifying data for each record", action="store_true")
    parser.add_argument("-t", "--type", help="limit to given <record-type>s", nargs="+", metavar="<record-type>")
    parser.add_argument("--diff_added", help="report records in plugin2 that do not exist in plugin1", action="store_true")
    parser.add_argument("--diff_removed", help="report records in plugin1 that do not exist in plugin2", action="store_true")
    parser.add_argument("--diff_ignore_changed", help="do not report changes between records that exist in plugin1 and plugin2", action="store_true")
    args = parser.parse_args()
    if args.type:
        args.type = [x.upper() for x in args.type]
    main(args)

