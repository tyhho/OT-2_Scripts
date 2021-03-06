# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 19:51:01 2020

@author: Trevor Ho
"""

from opentrons import protocol_api

#%%

# metadata
metadata = {
    'protocolName': 'Colony Plating Prototype',
    'author': 'Trevor Y. H. Ho <trevor.ho@ed.ac.uk>',
    'description': 'Transfer diluted bacteria from 96-well PCR plate to agar plate. \
        Prototype: Tip does not get changed when going 10-fold dilution up',
    'apiLevel': '2.6'
}

#%% 

def run(protocol: protocol_api.ProtocolContext):

    slots_map = {
            # '1':'corning_96_wellplate_360ul_flat',
            '4':'starlabpcrplateonws_96_wellplate_350ul', # no change tip
            # '5':'starlabpcrplateonws_96_wellplate_350ul', # change tip
            '1':'gbocellstaronewellagarplate_96_wellplate_10ul', # no change tip
            # '8':'gbocellstaronewellagarplate_96_wellplate_10ul' # change tip
            }
    
    # Configure tip racks and pipette
    
    # r_pipette_name = 'p300_single'
    # r_tiprack_slots = ['4']
    # r_tiprack_name = 'opentrons_96_tiprack_300ul'
    
    l_pipette_name = 'p10_multi'
    l_tiprack_slots = ['2']
    l_tiprack_name = 'geb_96_tiprack_10ul'
    
    labware_items = {}
    for slot, labware_item in slots_map.items():
        labware_items.update({slot:protocol.load_labware(labware_item, slot)})
    
    # r_tip_racks = [protocol.load_labware(r_tiprack_name, slot) for slot in r_tiprack_slots]
    l_tip_racks = [protocol.load_labware(l_tiprack_name, slot) for slot in l_tiprack_slots]
    
    # r_pipette = protocol.load_instrument(instrument_name = r_pipette_name,
    #     mount = 'right', tip_racks = r_tip_racks)
    l_pipette = protocol.load_instrument(instrument_name = l_pipette_name,
        mount = 'left', tip_racks = l_tip_racks)
    
    # 1 plate = 1 min 54 secs
    l_pipette.pick_up_tip()
    for i in reversed(range(12)):
        l_pipette.transfer(
            3, # transfer volume
            labware_items['4'].wells()[i * 8], # source
            labware_items['1'].wells()[i * 8], # dest,
            new_tip='never'
            )
    l_pipette.drop_tip()
    
    return protocol.commands()

# The extra part: programmatically get a simulation ProtocolContext, so we can run this
# as a normal Python script and have everything in the run function get executed.
#
# This part should be removed or commented out before uploading to a real OT-2.

# import json
# extra_labware_list = [
#     'starlabpcrplateonws_96_wellplate_350ul',
#     'gbocellstaronewellagarplate_96_wellplate_10ul'
#     ]

# extra_labware = {}
# for labware_name in extra_labware_list:
#     labware_json_fn = labware_name + '.json'
#     with open(labware_json_fn) as f: labware_data = json.load(f)
#     extra_labware.update({labware_name:labware_data})

# from opentrons.simulate import get_protocol_api
# protocol = get_protocol_api(version=metadata['apiLevel'], extra_labware=extra_labware)
# commands = run(protocol)

# for c in commands:
#     print(c)