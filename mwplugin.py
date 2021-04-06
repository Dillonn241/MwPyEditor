import argparse
import struct
import sys
import time
from collections import defaultdict

import mwglobals
import mwjobs
from record import (mwacti, mwalch, mwappa, mwarmo, mwbody, mwbook, mwbsgn, mwcell, mwclas, mwclot, mwcont, mwcrea,
                    mwdial, mwdoor, mwench, mwfact, mwglob, mwgmst, mwinfo, mwingr, mwland, mwlevc, mwlevi, mwligh,
                    mwlock, mwltex, mwmgef, mwmisc, mwnpc_, mwpgrd, mwprob, mwrace, mwregn, mwrepa, mwscpt, mwskil,
                    mwsndg, mwsoun, mwspel, mwsscr, mwstat, mwtes3, mwweap)

auto_load_masters = True


def init():
    """Choose at most one: list of records loaded by default for every plugin. TES3 should always be loaded."""
    # mwglobals.default_records = mwglobals.RECORDS_MIN # minimum types required for autocalc: MGEF, CLAS, RACE, SKIL
    # mwglobals.default_records = mwglobals.RECORDS_MOST # all types except: DIAL, INFO, CELL, LAND
    mwglobals.default_records = mwglobals.RECORDS_ALL  # all types

    """Expand list of records loaded by default for every plugin."""
    mwglobals.default_records += []

    """Choose any: load large data for CELL and LAND."""
    mwcell.init_references = True  # statics and other references placed in the world
    # mwland.init_lod = True # lod to show global map
    # mwland.init_terrain = True # normals, heights, colors, and textures of landscape (long load time)

    """Choose any: run algorithms to autocalc stats for ALCH, ENCH, SPEL, and NPC_."""
    mwalch.MwALCH.do_autocalc = True  # requires MGEF
    mwench.MwENCH.do_autocalc = True  # requires MGEF
    mwspel.MwSPEL.do_autocalc = True  # requires MGEF
    mwnpc_.MwNPC_.do_autocalc = True  # requires CLAS, RACE, SKIL

    """Load any plugins you want. Masters are automatically loaded."""
    # Vanilla
    load_plugin('Morrowind.esm')
    # load_plugin('Tribunal.esm')
    # load_plugin('Bloodmoon.esm')

    # DLC
    # load_plugin('adamantiumarmor.esp')
    # load_plugin('AreaEffectArrows.esp')
    # load_plugin('bcsounds.esp')
    # load_plugin('EBQ_Artifact.esp')
    # load_plugin('entertainers.esp')
    # load_plugin('LeFemmArmor.esp')
    # load_plugin('master_index.esp')
    # load_plugin('Siege at Firemoth.esp')

    # Tamriel Data
    # load_plugin('Tamriel_Data_6.esm')
    # load_plugin('Tamriel_Data_7.esm')
    # load_plugin('Tamriel_Data_7.1.esm')
    # load_plugin('Tamriel_Data.esm')
    # load_plugin('TD_Addon.esp')

    # Released versions of province mods
    # load_plugin('TR_Mainland_1809.esm')
    # load_plugin('TR_Mainland_1912.esm')
    # load_plugin('TR_Mainland_2002.esm')
    # load_plugin('Cyrodiil_Main_0.2.esm')
    # load_plugin('Sky_Main_02.esp')
    # load_plugin('Sky_Main_1812.esm')
    # load_plugin('Sky_Main_1903.esm')
    # load_plugin('Sky_Main_2001.esm')

    # Tamriel Rebuilt
    # load_plugin('TR_Mainland.esp')
    # load_plugin('TR_Factions.esp')
    # load_plugin('TR_Travels.esp')
    # load_plugin('TR_Travels_(Preview_and_Mainland).esp')
    # load_plugin('TR_Andothren_v0067.ESP')
    # load_plugin('TR_RorynsBluff_v0213.esp')
    # load_plugin('TR_ArmunAshlands_v0052.ESP')
    # load_plugin('TR_SouthernVelothis_v.0011.esp')
    # load_plugin('TR_ThirrValley_v0073.ESP')
    # load_plugin('TR_Kartur_v0022.ESP')
    # load_plugin('TR_RestExterior.esp')
    # load_plugin('TR_ShipalShin_v0004.ESP')

    # Skyrim: Home of the Nords
    # load_plugin('Sky_Main_2021_03_29.ESP')
    # load_plugin('Sky_Markarth_2021_01_31.ESP')
    # load_plugin('Sky_Falkheim_2021_01_31.ESP')

    # Province: Cyrodiil
    # load_plugin('Cyrodiil_Main_2021_03_12b.ESP')
    # load_plugin('PC_Anvil_v0073.ESP')
    # load_plugin('PC_Sutch_v0017.ESP')

    save_plugin('test.esp', 'Morrowind.esm')

    print()


def handle_args(args):

    if args.command == 'diff':
        args_diff(args)
    elif args.command == 'dump':
        args_dump(args)


def args_diff(args):
    if len(args.plugins) != 2:
        sys.exit("Exactly two plugins can be diffed!")

    plugin1 = args.plugins[0]  # 'Tamriel_Data_6.esm'
    plugin2 = args.plugins[1]  # 'Tamriel_Data.esm'
    record_types = mwglobals.RECORDS_MIN + args.type if args.type else mwglobals.RECORDS_ALL
    load_plugin(plugin1, records_to_load=record_types)
    load_plugin(plugin2, records_to_load=record_types)
    print(f"# Diff plugin {plugin1} with {plugin2}: #\n")

    diff_changed = not args.diff_ignore_changed if args.diff_ignore_changed else True
    diff_equal = args.diff_equal if args.diff_equal else False
    diff_added = args.diff_added if args.diff_added else False
    diff_removed = args.diff_removed if args.diff_removed else False
    for rcd_type in record_types:
        print(f"## Diff record type {rcd_type}: ##\n")
        diff_plugins(plugin1, plugin2, rcd_type, changed=diff_changed, equal=diff_equal, added=diff_added,
                     removed=diff_removed)


def args_dump(args):
    for plugin in args.plugins:
        record_types = mwglobals.RECORDS_MIN + args.type if args.type else mwglobals.RECORDS_ALL
        load_plugin(plugin, records_to_load=record_types)
        print(f"# Dump plugin {plugin}: #\n")
        for rcd_type in record_types:
            print(f"## Dump record type {rcd_type}: ##\n")
            if args.list:
                for rcd in mwglobals.plugin_records[plugin][rcd_type]:
                    print(rcd)
            else:
                for rcd in mwglobals.plugin_records[plugin][rcd_type]:
                    print(rcd.record_details())


def load_plugin(file_name, records_to_load=None, masters_loaded=None):
    # use default_records if no argument is provided for records_to_load
    if not records_to_load:
        records_to_load = mwglobals.default_records
    # if automatically loading masters, TES3 is required
    if auto_load_masters:
        if 'TES3' not in records_to_load:
            records_to_load.append('TES3')
        # keep track of masters loaded to avoid chain reaction
        if not masters_loaded:
            masters_loaded = []
    # DIAL should always be loaded with INFO
    if 'INFO' in records_to_load and 'DIAL' not in records_to_load:
        records_to_load.append('DIAL')
    # if the plugin has been loaded before, only load what is still unloaded
    if file_name in mwglobals.plugin_records:
        records_to_load = [x for x in records_to_load if x not in mwglobals.plugin_records[file_name]]
    # otherwise, set up a record list for this plugin in plugin_records
    else:
        mwglobals.plugin_records[file_name] = defaultdict(list)
    # nothing to do if records_to_load is empty
    if not records_to_load:
        return

    # read the plugin file
    with open(mwglobals.DATA_PATH + file_name, mode='rb') as file:
        def load_record():
            # 4 bytes make up a header
            record_type, length, unknown, flags = struct.unpack('<4siii', header)
            record_type = record_type.decode('mbcs')
            length_left = length
            # skip record if it's not a type being loaded
            if record_type not in records_to_load:
                file.seek(length, 1)
                return
            # create record and associate it with this plugin name
            record = create_record(record_type)
            record.file_name = file_name
            # add to global record data structures
            mwglobals.records[record_type].append(record)
            mwglobals.ordered_records.append(record)
            mwglobals.plugin_records[file_name][record_type].append(record)
            # split up the data into subrecords
            while length_left > 0:
                subtype, sublength = struct.unpack('<4si', file.read(8))
                subtype = subtype.decode('mbcs')
                record.add_subrecord(subtype, subdata=file.read(sublength))
                length_left -= 8 + sublength
            # send flags and data off to class to parse
            record.load_flags(flags)
            record.load()
            record.load_deleted()
            return record

        # if setting on, automatically load records from masters; skip if TES3 has been loaded previously
        if auto_load_masters and 'TES3' in records_to_load:
            if header := file.read(16):  # same as single iteration of load_record loop
                for master in load_record().masters:  # first record must be TES3
                    if master not in masters_loaded:
                        masters_loaded.append(master)
                        load_plugin(master, records_to_load=records_to_load, masters_loaded=masters_loaded)
        # print a loading message
        print(f"** Loading {file_name}: {records_to_load} **")
        # load_record loop
        while header := file.read(16):
            load_record()


def save_plugin(file_name, active_file, *merge_files):
    print(file_name)
    files = (active_file,) + merge_files
    with open(file_name, mode='wb') as file:
        for record in mwglobals.ordered_records:
            if record.file_name in files:
                flags = record.save_flags()
                if hasattr(record, 'save'):  # temporary until all are implemented
                    record.save()
                length = 0
                for subrecord in record.ordered_subrecords:
                    length += 8 + len(subrecord.data)
                file.write(struct.pack('<4siii', record.get_record_type().encode('mbcs'), length, 0, flags))
                for subrecord in record.ordered_subrecords:
                    file.write(struct.pack('<4si', subrecord.record_type.encode('mbcs'), len(subrecord.data)))
                    file.write(subrecord.data)


def create_record(record_type):
    if record_type == 'TES3':
        return mwtes3.MwTES3()
    elif record_type == 'GMST':
        return mwgmst.MwGMST()
    elif record_type == 'GLOB':
        return mwglob.MwGLOB()
    elif record_type == 'CLAS':
        return mwclas.MwCLAS()
    elif record_type == 'FACT':
        return mwfact.MwFACT()
    elif record_type == 'RACE':
        return mwrace.MwRACE()
    elif record_type == 'SOUN':
        return mwsoun.MwSOUN()
    elif record_type == 'SKIL':
        return mwskil.MwSKIL()
    elif record_type == 'MGEF':
        return mwmgef.MwMGEF()
    elif record_type == 'SCPT':
        return mwscpt.MwSCPT()
    elif record_type == 'REGN':
        return mwregn.MwREGN()
    elif record_type == 'BSGN':
        return mwbsgn.MwBSGN()
    elif record_type == 'LTEX':
        return mwltex.MwLTEX()
    elif record_type == 'STAT':
        return mwstat.MwSTAT()
    elif record_type == 'DOOR':
        return mwdoor.MwDOOR()
    elif record_type == 'MISC':
        return mwmisc.MwMISC()
    elif record_type == 'WEAP':
        return mwweap.MwWEAP()
    elif record_type == 'CONT':
        return mwcont.MwCONT()
    elif record_type == 'SPEL':
        return mwspel.MwSPEL()
    elif record_type == 'CREA':
        return mwcrea.MwCREA()
    elif record_type == 'BODY':
        return mwbody.MwBODY()
    elif record_type == 'LIGH':
        return mwligh.MwLIGH()
    elif record_type == 'ENCH':
        return mwench.MwENCH()
    elif record_type == 'NPC_':
        return mwnpc_.MwNPC_()
    elif record_type == 'ARMO':
        return mwarmo.MwARMO()
    elif record_type == 'CLOT':
        return mwclot.MwCLOT()
    elif record_type == 'REPA':
        return mwrepa.MwREPA()
    elif record_type == 'ACTI':
        return mwacti.MwACTI()
    elif record_type == 'APPA':
        return mwappa.MwAPPA()
    elif record_type == 'LOCK':
        return mwlock.MwLOCK()
    elif record_type == 'PROB':
        return mwprob.MwPROB()
    elif record_type == 'INGR':
        return mwingr.MwINGR()
    elif record_type == 'BOOK':
        return mwbook.MwBOOK()
    elif record_type == 'ALCH':
        return mwalch.MwALCH()
    elif record_type == 'LEVI':
        return mwlevi.MwLEVI()
    elif record_type == 'LEVC':
        return mwlevc.MwLEVC()
    elif record_type == 'CELL':
        return mwcell.MwCELL()
    elif record_type == 'LAND':
        return mwland.MwLAND()
    elif record_type == 'PGRD':
        return mwpgrd.MwPGRD()
    elif record_type == 'SNDG':
        return mwsndg.MwSNDG()
    elif record_type == 'DIAL':
        return mwdial.MwDIAL()
    elif record_type == 'INFO':
        info = mwinfo.MwINFO()
        last_dial = mwglobals.records['DIAL'][-1]
        last_dial.infos.append(info)
        info.dial = last_dial
        return info
    elif record_type == 'SSCR':
        return mwsscr.MwSSCR()


def diff_plugins(plugin1, plugin2, record_type, changed=True, equal=False, added=False, removed=False):
    object_ids1 = {}
    object_ids2 = {}
    for record in mwglobals.records[record_type]:
        if record.file_name == plugin1:
            object_ids1[record.get_id()] = record
        elif record.file_name == plugin2:
            object_ids2[record.get_id()] = record

    if changed or equal:
        for record in mwglobals.records[record_type]:
            if record.file_name == plugin1:
                if record.get_id() in object_ids2:
                    record2 = object_ids2[record.get_id()]
                    diff = record.diff(record2)
                    if changed and diff:
                        print(diff)
                        print()
                    if equal and not diff:
                        print(f"Identical records: {record.get_id()} = {record2.get_id()}")
                        print()

    if added:
        for record in mwglobals.records[record_type]:
            if record.file_name == plugin2:
                if record.get_id() not in object_ids1:
                    print("\nAdded", record)
                    print(record.record_details())
                    print()

    if removed:
        for record in mwglobals.records[record_type]:
            if record.file_name == plugin1:
                if record.get_id() not in object_ids2:
                    print("\nRemoved", record)
                    print()


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
                        print('-', loc)
                for loc in locations2:
                    if loc not in locations1:
                        if first_print:
                            print(record)
                            first_print = False
                        print('+', loc)


def init_args():
    parser = argparse.ArgumentParser(description="""Analyze a plugin file.
                                                 \n\nThe following commands are available:
                                                 \ndiff\tfind the difference between two plugins
                                                 \ndump\toutput readable record data""",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('command', help="name of the action to take")
    parser.add_argument('plugins', nargs='+', help="list of plugins to load and provide as arguments")
    parser.add_argument('-t', '--type', nargs='+', help="limit to given <record type>s", metavar="<record type>")
    parser.add_argument('-l', '--list', action='store_true', help="show only identifying data for each record")
    parser.add_argument('--diff_ignore_changed', action='store_true', help="""do not report changes between records that
                                                                           exist in plugin1 and plugin2""")
    parser.add_argument('--diff_equal', action='store_true', help="""report records in plugin1 that are identical in
                                                                    plugin2""")
    parser.add_argument('--diff_added', action='store_true', help="""report records in plugin2 that do not exist in
                                                                  plugin1""")
    parser.add_argument('--diff_removed', action='store_true', help="""report records in plugin1 that do not exist in
                                                                    plugin2""")
    args = parser.parse_args()
    if args.type:
        args.type = [x.upper() for x in args.type]
    return args


def main():
    start_time = time.time()
    init()
    if len(sys.argv) > 2 or '-h' in sys.argv or '--help' in sys.argv:
        args = init_args()
        handle_args(args)

    # Python commands
    """
    mwjobs.find_creatures(file='files/SHOTN_Creas.csv')
    mwjobs.ref_map(file='files/SHOTN_Creas.csv', img='files/SHOTN_CellExport.png', top=23, bottom=-3, left=-120,
                   right=-94)
    mwjobs.exterior_doors(file='files/PC_Doors.csv')
    mwjobs.ref_map(file='files/PC_Doors.csv', img='files/PC_CellExport.png', top=-35, bottom=-58, left=-141,right=-108)
    """

    time_spent = time.time() - start_time
    print(f"\n** Time spent: {time_spent:.3f} seconds **")


if __name__ == '__main__':
    main()
