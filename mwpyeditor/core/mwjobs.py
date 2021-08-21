import collections
import tkinter as tk

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MultipleLocator

from mwpyeditor.core import mwglobals, mwutil
from mwpyeditor.record import mwcrea, mwdoor, mwlevc, mwnpc_


"""
ASSET USAGE
"""


def deprecated_check():
    deprecated_ids = []
    for rcd_type in mwglobals.records:
        for record in mwglobals.records[rcd_type]:
            if hasattr(record, 'name') and record.name and "deprecated" in record.name.lower():
                deprecated_ids.append(record.id_)
            elif hasattr(record, 'model') and record.model and "help_deprec" in record.model.lower():
                deprecated_ids.append(record.id_)
    print("## Deprecated Cell Refs: ##")
    for cell in mwglobals.records['CELL']:
        for ref in cell.references:
            if ref.id_ in deprecated_ids:
                print(f"{cell}: {ref.id_}")
    print("\n## Deprecated NPC Items: ##")
    for npc in mwglobals.records['NPC_']:
        for item in npc.items:
            if item in deprecated_ids:
                print(f"{npc.id_}: {item}")
    print("\n## Deprecated NPC Spells: ##")
    for npc in mwglobals.records['NPC_']:
        for spell in npc.spells:
            if spell in deprecated_ids:
                print(f"{npc.id_}: {spell}")
    print("\n## Deprecated Creature Items: ##")
    for creature in mwglobals.records['CREA']:
        for item in creature.items:
            if item in deprecated_ids:
                print(f"{creature.id_}: {item}")
    print("\n## Deprecated Creature Spells: ##")
    for creature in mwglobals.records['CREA']:
        for spell in creature.spells:
            if spell in deprecated_ids:
                print(f"{creature.id_}: {spell}")
    print("\n## Deprecated Container Items: ##")
    for container in mwglobals.records['CONT']:
        for item in container.items:
            if item in deprecated_ids:
                print(f"{container.id_}: {item}")
    print("\n## Deprecated IDs in Scripts: ##")
    for script in mwglobals.records['SCPT']:
        for id_ in deprecated_ids:
            if id_ in script.text:
                print(f"{script.id_}: {id_}")
    print("\n## Deprecated Leveled List Items: ##")
    for lev_item in mwglobals.records['LEVI']:
        for item in lev_item.items:
            if item.id_ in deprecated_ids:
                print(f"{lev_item.id}: {item.id_}")
    print("\n## Deprecated Leveled List Creatures: ##")
    for lev_crea in mwglobals.records['LEVC']:
        for creature in lev_crea.creatures:
            if creature.id_ in deprecated_ids:
                print(f"{lev_crea.id_}: {creature.id_}")
    print()


def find_usage(id_):
    for npc in mwglobals.records['NPC_']:
        for item in npc.items:
            if item == id_:
                print(npc)
                break
    for creature in mwglobals.records['CREA']:
        for item in creature.items:
            if item == id_:
                print(creature)
                break
    for cell in mwglobals.records['CELL']:
        for ref in cell.references:
            if ref.id_ == id_:
                print(cell)
                break
    for container in mwglobals.records['CONT']:
        for item in container.items:
            if item == id_:
                print(container)
                break
    for leveled_list in mwglobals.records['LEVI']:
        for item in leveled_list.items:
            if item.id_ == id_:
                print(leveled_list)
                break
    for leveled_creature in mwglobals.records['LEVC']:
        for creature in leveled_creature.creatures:
            if creature.id_ == id_:
                print(leveled_creature)
                break
    for script in mwglobals.records['SCPT']:
        if id_ in script.text:
            print(script)


def find_item_usage(id_, file_names=None):
    usages = []
    for npc in mwglobals.records['NPC_']:
        if not file_names or npc.file_name in file_names:
            for item in npc.items:
                if item == id_:
                    count = npc.items[item]
                    if count == 1:
                        usages.append(f"Carried by {{{{{mwutil.mod_shortcut(npc)}|{npc.name}}}}}")
                    else:
                        usages.append(f"Carried by {{{{{mwutil.mod_shortcut(npc)}|{npc.name}}}}} (&times;{count})")
                    break
    for creature in mwglobals.records['CREA']:
        if not file_names or creature.file_name in file_names:
            for item in creature.items:
                if item == id_:
                    count = creature.items[item]
                    if count == 1:
                        usages.append(f"Carried by {{{{{mwutil.mod_shortcut(creature)}|{creature.name}}}}}")
                    else:
                        usages.append(f"""Carried by {{{{{mwutil.mod_shortcut(creature)}|{creature.name}}}}}
                                       (&times;{count})""")
                    break
    for cell in mwglobals.records['CELL']:
        if not file_names or cell.file_name in file_names:
            count = 0
            for ref in cell.references:
                if ref.id_ == id_:
                    count += 1
            if count == 1:
                usages.append(str(cell))
            elif count > 1:
                usages.append(f"{cell} (&times;{count})")
    for container in mwglobals.records['CONT']:
        if not file_names or container.file_name in file_names:
            for item in container.items:
                if item == id_:
                    for loc in find_item_usage(container.id_, file_names=file_names):
                        count = container.items[item]
                        if count == 1:
                            usages.append(f"{loc} ({container.name})")
                        else:
                            usages.append(f"{loc} (&times;{count}, in {container.name})")
                    break
    for leveled_list in mwglobals.records['LEVI']:
        if not file_names or leveled_list.file_name in file_names:
            for item in leveled_list.items:
                if item.id_ == id_:
                    usages.append(leveled_list.id_)
                    break
    return usages


"""
DIALOGUE
"""

def journal_list(drop=True):
    journaldata = []
    for info in mwglobals.records["INFO"]:
        if info.quest_name:
            journaldata.append([info.dial.id_, info.response])
    journaldata = pd.DataFrame(journaldata, columns=['ID', 'Name'])
    journaldata = journaldata.drop_duplicates(subset=['ID'], keep='first')
    if drop:
        journaldata = journaldata.drop_duplicates(subset=['Name'], keep='first')
    return journaldata

def npc_freq():
    npcdata = []
    for cell in mwglobals.records["CELL"]:
        for ref in cell.references:
            try:
                obj = mwglobals.object_ids[ref.id_]
            except:
                print("Object not found: " + ref.id_)
            finally:
                if isinstance(obj, mwnpc_.MwNPC_) and not ref.deleted:
                    npcfilter = cell.get_region()
                    if cell.id_ != '':
                        npcfilter = cell.id_.split(',')[0]
                    npcdata.append([obj.id_, npcfilter])
    npcs = pd.DataFrame(npcdata, columns=['Name', 'Cell'])
    npcs['Freq'] = npcs.groupby('Name')['Name'].transform('count')
    return npcs

def choice_tree(): # WIP
    choicetree = []
    for info in mwglobals.records["INFO"]:
        fromchoice = []
        tochoice = None
        if info.result is not None:
            if "Choice" in info.result or "choice" in info.result:
                dialresult = info.result.replace(',', '')
                dialresult = dialresult.split('\r\n')
                dialresult = [s for s in dialresult if "Choice" in s]
                dialresult = ' '.join(dialresult)
                dialresult = dialresult.split(' ')
                dialresult = list(set(dialresult))
                tochoice = [i for i in dialresult if i.isnumeric()]
                tochoice = ','.join(tochoice)
                tochoice = str(dialresult)
        for ifilter in info.func_var_filters:
            if ifilter.get_function() == 'Choice' or ifilter.get_function() == 'choice':
                fromchoice.append(ifilter.get_operator() + str(ifilter.intv))
        if fromchoice or tochoice is not None:
            choicetree.append([info.dial, info.id_, fromchoice, tochoice])
    choicetree = pd.DataFrame(choicetree, columns=['Topic', 'ID', 'From', 'To'])
    # dialpivot = choicetree.groupby(['Topic'])['To'].apply(lambda x: ','.join(item for item in x if item))
    # dialpivot['Choices'] = dialpivot['Choices'].split(',')
    return choicetree

def dump_dialogue():
    cols = ['Topic', 'Type', 'Disp', 'Actor', 'Cell', 'Entry', 'Sex', 'Race', 'Class', 'Faction', 'Rank', 'PCFaction', 'PCRank', 'FunVar', 'Result', 'ID']
    data = []
    for info in mwglobals.records["INFO"]:
        if info.rank == 255:
            info.rank = None
        if info.pc_rank == 255:
            info.pc_rank = None
        data.append(
            [info.dial.id_, info.dial.get_type(), info.disposition, info.actor, info.cell, info.response, info.sex, info.race, info.class_,
             info.faction, info.rank, info.pc_faction, info.pc_rank, info.func_var_filters, info.result, info.id_])
    entries = pd.DataFrame(data, columns=cols)
    return entries

def dialogue_analysis(): #WIP
    dial = dump_dialogue()
    npcs = npc_freq()
    journaldata = journal_list(drop=False)
    journallist = list(journaldata['ID'])
    cellfilters = []
    npcfilters = []
    questfilters = []
    dial['Merge'] = dial[dial.columns].astype(str).apply(lambda x: ','.join(x), axis=1)
    for ind in dial.index:
        if dial['Actor'][ind] is not None:
            npcfilters.append(dial['Actor'][ind])
        else:
            npcfilters.append("")
        if dial['Cell'][ind] is not None:
            cellfilters.append(dial['Cell'][ind].split(',')[0])
        elif dial['Actor'][ind] is not None and npcs[npcs['Name'] == dial['Actor'][ind]]['Freq'].min() == 1:
            if npcs.loc[npcs['Name'] == dial['Actor'][ind], 'Cell'].item() != "":
                cellfilters.append(npcs.loc[npcs['Name'] == dial['Actor'][ind], 'Cell'].item())
        else:
            cellfilters.append("")
        journals = set()
        for journal in journallist:
            if dial['Merge'][ind].find(journal) >= 0:
                journals.add(journaldata.loc[journaldata['ID'] == journal, 'Name'].item())
        questfilters.append(";".join(journals))
    dial['CellFilter'] = cellfilters
    dial['NPCFilter'] = npcfilters
    dial['QuestFilter'] = questfilters
    # choicetree = choice_tree()
    return dial.drop(columns=['Merge'])


"""
MAPPING
"""


def exterior_doors(file):
    doorfile = open('../exceptions/mwdoor.txt', 'r')
    doorlist = doorfile.read().splitlines()
    cols = ['Name', 'GridX', 'GridY', 'PosX', 'PosY', 'ID', 'Check']
    data = []
    for cell in mwglobals.exterior_cells.values():
        for ref in cell.references:
            obj = mwglobals.object_ids[ref.id_]
            if isinstance(obj, mwdoor.MwDOOR) and not ref.deleted:
                if ref.door_cell:
                    check = 1
                elif obj.id_ in doorlist:
                    check = 2
                else:
                    check = 0
                data.append([cell.get_name(), cell.grid_x, cell.grid_y, ref.pos_x, ref.pos_y, obj.id_, check])
    doors = pd.DataFrame(data, columns=cols)
    doors.to_csv(file, index=False, header=True)


def find_creatures(file):
    creafile = open('../exceptions/mwcrea.txt', 'r')
    crealist = creafile.read().splitlines()
    levcfile = open('../exceptions/mwlevc.txt', 'r')
    levclist = levcfile.read().splitlines()
    cols = ['Name', 'GridX', 'GridY', 'PosX', 'PosY', 'ID', 'Check']
    data = []
    for cell in mwglobals.exterior_cells.values():
        for ref in cell.references:
            obj = mwglobals.object_ids[ref.id_]
            if not ref.deleted:
                if obj.id_ in crealist or obj.id_ in levclist:
                    check = 3
                    data.append([cell.get_name(), cell.grid_x, cell.grid_y, ref.pos_x, ref.pos_y, obj.id_, check])
                elif isinstance(obj, mwcrea.MwCREA):
                    check = 0
                    data.append([cell.get_name(), cell.grid_x, cell.grid_y, ref.pos_x, ref.pos_y, obj.id_, check])
                elif isinstance(obj, mwlevc.MwLEVC):
                    check = 1
                    data.append([cell.get_name(), cell.grid_x, cell.grid_y, ref.pos_x, ref.pos_y, obj.id_, check])
    creas = pd.DataFrame(data, columns=cols)
    creas.to_csv(file, index=False, header=True)


def ref_map(file, img, top, bottom, left, right):
    ref_locs = pd.read_csv(file)
    ref_locs = ref_locs[ref_locs.Check != 2]
    ref_locs.PosX = ref_locs.PosX / pow(2, 13)
    ref_locs.PosY = ref_locs.PosY / pow(2, 13)
    ref_locs['Check'] = ref_locs['Check'].map({0: '#00FFFF', 1: '#FF0000'})
    cellexp = plt.imread(img)
    h, w, _ = cellexp.shape
    h = h / 256
    w = w / 256
    fig, ax = plt.subplots()
    le = ax.figure.subplotpars.left
    ri = ax.figure.subplotpars.right
    to = ax.figure.subplotpars.top
    bo = ax.figure.subplotpars.bottom
    figw = float(w) / (ri - le)
    figh = float(h) / (to - bo)
    ax.figure.set_size_inches(figw, figh)
    ax.grid(color='grey', linestyle='-', linewidth=2, alpha=0.5, which='both')
    ax.get_xaxis().set_minor_locator(MultipleLocator(1))
    ax.get_yaxis().set_minor_locator(MultipleLocator(1))
    ax.imshow(cellexp, extent=(left, right + 1, bottom, top + 1))
    ax.scatter(ref_locs.PosX, ref_locs.PosY, c = ref_locs.Check, marker='.', s=4, edgecolor=None)
    ax.legend([],[], frameon=False)
    del ref_locs
    del cellexp
    fig.savefig("files/Refs.png", dpi=256, bbox_inches='tight')


def view_heightmap(window_width=800, window_height=600, downscale=5, lod=False):
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    for land in mwglobals.records['LAND']:
        if land.grid_x < min_x:
            min_x = land.grid_x
        elif land.grid_x > max_x:
            max_x = land.grid_x
        if land.grid_y < min_y:
            min_y = land.grid_y
        elif land.grid_y > max_y:
            max_y = land.grid_y
    if lod:
        cell_size = mwglobals.LAND_LOD_SIZE
    else:
        cell_size = int(mwglobals.LAND_SIZE / downscale)
    world_width = (max_x - min_x) * cell_size
    world_height = (max_y - min_y) * cell_size
    half_width = int(world_width / 2)
    half_height = int(world_height / 2)

    root = tk.Tk()
    frame = tk.Frame(root)
    frame.grid(row=0, column=0)

    canvas = tk.Canvas(frame, width=window_width, height=window_height, scrollregion=(0, 0, world_width, world_height))
    img = tk.PhotoImage(width=world_width, height=world_height)
    for land in mwglobals.records['LAND']:
        if not lod:
            land.load_terrain()
        x = (land.grid_x - min_x) * cell_size
        y = (max_y - land.grid_y) * cell_size
        for i in range(cell_size):
            for j in range(cell_size):
                if lod:
                    height = land.lod_heights[i + j * mwglobals.LAND_LOD_SIZE]
                else:
                    height = int(land.heights[i * downscale + j * downscale * mwglobals.LAND_SIZE] / 10)
                if height >= 0:
                    color = f"#{height:02x}{height:02x}{height:02x}"
                else:
                    darker = 255 + height
                    color = f"#{darker:02x}{darker:02x}{255:02x}"
                img.put(color, (x + i, y + cell_size - j))
    canvas.create_image((half_width, half_height), image=img, state="normal")

    hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
    hbar.config(command=canvas.xview)
    hbar.pack(side=tk.BOTTOM, fill=tk.X)
    vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    vbar.config(command=canvas.yview)
    vbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    canvas.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

    root.mainloop()


"""
WIKI DOCUMENTATION
"""


def diff_locations(plugin1, file_names1, plugin2, file_names2, record_type):
    file_names1 += [plugin1]
    file_names2 += [plugin2]
    object_ids2 = {record.get_id(): record
                   for record in mwglobals.records[record_type]
                   if record.file_name == plugin2}

    for record in mwglobals.records[record_type]:
        if record.file_name == plugin1:
            if record.get_id() in object_ids2:
                first_print = True
                record2 = object_ids2[record.get_id()]
                locations1 = find_item_usage(record.get_id(), file_names=file_names1)
                locations2 = find_item_usage(record2.get_id(), file_names=file_names2)
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


def region_location_changes(plugin1, plugin2):
    locations1 = []
    locations2 = []
    for cell in mwglobals.records['CELL']:
        if not cell.is_interior:
            if cell.file_name == plugin1:
                for ref in cell.references:
                    if ref.door_cell:
                        locations1.append(f"{cell.get_region()}: {ref.door_cell}")
            elif cell.file_name == plugin2:
                for ref in cell.references:
                    if ref.door_cell:
                        locations2.append(f"{cell.get_region()}: {ref.door_cell}")
    for loc in locations1:
        if loc not in locations2:
            print(f"-{loc}")
    for loc in locations2:
        if loc not in locations1:
            print(f"+{loc}")


def faction_members(faction, file_name):
    npcs = [npc for npc in mwglobals.records['NPC_'] if npc.faction == faction and npc.file_name == file_name]
    npcs.sort(key=lambda x: x.name)
    for npc in npcs:
        print("|-")
        print(f"!{{{{TR3|{npc.name}}}}}")
        data = [f"""|{npc.get_sex_template()}||[[Morrowind:{npc.get_wiki_race()}|{npc.get_wiki_race()}]]||[[Morrowind:
                {npc.get_wiki_class()}|{npc.class_}]]||{npc.faction_rank} {npc.get_faction_rank_name()}||"""]
        cell_str = []
        for cell in mwglobals.records['CELL']:
            for ref in cell.references:
                if ref.id_ == npc.id_:
                    cell_str.append(str(cell))
                    break
        data.append(f"{'<br>'.join(sorted(cell_str))}||")
        service_str = []
        if (npc.service_weapons or npc.service_armor or npc.service_clothing or npc.service_books or
                npc.service_ingredients or npc.service_picks or npc.service_probes or npc.service_lights or
                npc.service_apparatus or npc.service_repair_items or npc.service_miscellaneous or
                npc.service_magic_items or npc.service_potions):
            service_str.append("{{TR3|Merchants|Merchant}}")
        if npc.service_spells:
            service_str.append("{{TR3|Spell Merchants|Spell Merchant}}")
        if npc.service_training:
            service_str.append("{{TR3|Trainers|Trainer}}")
        if npc.service_spellmaking:
            service_str.append("{{TR3|Spellmaker}}")
        if npc.service_enchanting:
            service_str.append("{{TR3|Enchanter}}")
        if npc.service_repair:
            service_str.append("{{TR3|Blacksmith|Blacksmith}}")
        data.append(', '.join(service_str))
        print(''.join(data))


def print_trainers_by_skill():
    trainers = {}
    for skill in mwglobals.SKILLS:
        trainers[skill] = []
    for npc in mwglobals.records['NPC_']:
        for skill, value in npc.trained_skills():
            trainers[skill] += [(npc, value)]
    for skill in trainers:
        trainers[skill] = sorted(trainers[skill], key=lambda x: x[1], reverse=True)
        print(skill)
        for trainer, value in trainers[skill]:
            print(trainer.name, value)
        print()


def journal_entries(file_name):
    quests = collections.defaultdict(list)
    for quest in mwglobals.records['DIAL']:
        if quest.file_name == file_name and quest.type_id == 4:  # Journal
            for info in quest.infos:
                if info.quest_name:
                    quests[info.response].append(quest)
                    break
    for name in quests:
        quest_list = quests[name]
        quest_list.sort(key=lambda x: x.id_)
        print(f"{name}\n==Quest Stages==\n{{{{MW Quest Stages Notes}}}}\n{{{{Journal Entries")
        for i in range(len(quest_list)):
            quest = quest_list[i]
            if i == 0:
                print(f"id={quest.id_}")
            else:
                print(f"|!||{quest.id_}")

            quest.infos.sort(key=lambda x: x.disposition)
            for info in quest.infos:
                if info.quest_name:
                    continue

                if info.quest_finished:
                    special = "fin"
                elif info.quest_restart:
                    special = "restart"
                else:
                    special = ""
                print(f"|{info.disposition}|{special}|{info.response}")
        print("}}\n")
