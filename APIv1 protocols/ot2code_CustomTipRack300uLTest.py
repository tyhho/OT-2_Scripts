# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 00:54:16 2020

@author: Trevor Ho
"""
# Import libraries for OT-2
from opentrons import labware, instruments,robot

tip_rack_name = 'tiprack-300ul-custom'
if tip_rack_name not in labware.list():
    custom_plate = labware.create(
        tip_rack_name,                    # name of you labware
        grid=(12, 8),                    # specify amount of (columns, rows)
        spacing=(9, 9),               # distances (mm) between each (column, row)
        diameter=3,                     # diameter (mm) of each well on the plate
        depth=10,                       # depth (mm) of each well on the plate
        volume=10
#        ,        offset=(14.3, 10.5, 65)
        )

# Put plates and racks onto the deck
slots_map = {
        '1':'opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap',
        }

dlw = {}
for slot, labware_item in slots_map.items():
    dlw.update({slot:labware.load(labware_item, slot)})

# Put tip boxes onto the deck

tip_slots = ['2']
tip_racks = []
for slot in tip_slots:
        tip_racks.append(labware.load('tiprack-10ul', slot))

# Configure the pipettes

pipette = instruments.P300_Single(
    mount='right',
    tip_racks=tip_racks
    )

# Set up the pipetting instruction
 
#%%    
## Execution of instructions
vol = 300

for tip_well in ['A1','A7','A12','D1','D7','D12','H1','H7','H12']:
    pipette.pick_up_tip(location = tip_racks[0].wells(tip_well))
    pipette.aspirate(vol, dlw['2'].wells('A1'))
    pipette.move_to(dlw['2'].wells('A1').top(10))
    pipette.dispense(vol,dlw['2'].wells('A1'))
    pipette.blow_out()
    pipette.drop_tip()

# Print out the commands step by step
for c in robot.commands():
    print(c)