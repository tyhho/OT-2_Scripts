# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 23:15:27 2019

@author: Trevor Ho

"""

from opentrons import labware, instruments, robot

#%%
def distributeNoBlowOut(pipette,vol_out,source,dests,disposal_vol=0,airgap=0,hover_over=-21):
    '''Distribute function with disposal volume but without blow out'''
    
    if airgap != 0 and disposal_vol !=0:
        raise ValueError('Air gap and disposal volume should not be used at the same time')
    
    if airgap !=0 and hover_over == 0:
        raise ValueError('Air gap use should be accompanied with hover_over')

    # Converts the list of destination wells from :WellSeries: into a list to permit .pop() function
    dests_all = list(dests.items.values())
    
    pipette_max_vol = pipette.max_volume
    
    if airgap <= 0 and (vol_out *2 + disposal_vol) <= pipette_max_vol:
    
    # Mode 1: 
    # Full description: So long as there are wells that have not received dispensed liquid (item still in dests_all), the function will try to calculate how many dispenses can be fit into one aspiration volume (one_trans_aspir_vol), and then perform the sub-distribution step. To keep track of the wells to be dispensed, the function pops a :Well: from dests_all and then add it to the list of one_trans_dests. The function stops tracking when there is no more :Well: in the dests_all list
    
    # The function changes tip for each sub-distribution step
            
        while dests_all:
        
            one_trans_aspir_vol = disposal_vol
            one_trans_dests = []
            
            # Calculate the maximum distributions that one aspiration can take
            while one_trans_aspir_vol + vol_out < pipette_max_vol:
                one_trans_dests.append(dests_all.pop(0))
                one_trans_aspir_vol = one_trans_aspir_vol + vol_out
                if not dests_all: break
                
            # Performs the actual distribution sub-step
            pipette.pick_up_tip()
            pipette.aspirate(one_trans_aspir_vol,source)
            for dest in one_trans_dests:
                if hover_over >=0:
                    pipette.dispense(vol_out,dest.top(hover_over))
                else:
                    pipette.dispense(vol_out,dest)
        
            pipette.drop_tip()

    # Mode 2: Air gap mode
    elif airgap > 0 and (vol_out * 2 + airgap) <= pipette_max_vol:
        
        pipette.pick_up_tip()
        while dests_all:
            
            one_trans_aspir_vol = 0
            one_trans_dests = []
            
            # Calculate the maximum distributions that one aspiration can take
            while one_trans_aspir_vol + vol_out + airgap < pipette_max_vol:
                one_trans_dests.append(dests_all.pop(0))
                one_trans_aspir_vol += vol_out
                if not dests_all: break
                one_trans_aspir_vol += airgap
                
            # Performs the actual distribution sub-step
            
            for dest in one_trans_dests:
                if dest != one_trans_dests[-1]:
                    pipette.aspirate(vol_out,source).air_gap(airgap)
                else:
                    pipette.aspirate(vol_out,source)
            
            for dest in one_trans_dests:
                if dest == one_trans_dests[0] or dest == one_trans_dests[-1]:
                    pipette.dispense((vol_out + (airgap/2)),dest.top(hover_over))
                else:
                    pipette.dispense((vol_out + airgap),dest.top(hover_over))
        pipette.drop_tip()
    
    # Mode 3:
    else:
        for dest in dests_all:    
            pipette.pick_up_tip()

            if vol_out > pipette_max_vol:
                vol_list = []
                vol_remaining = vol_out
                while vol_remaining > pipette_max_vol:
                    vol_list.append(pipette_max_vol)
                    vol_remaining -= pipette_max_vol
                vol_list.append(vol_remaining)
                
            else:
                vol_list = [vol_out]
                
            for vol in vol_list:
                if hover_over >=0:
                    pipette.transfer(
                    	vol,
                    	source,
                    	dest.top(hover_over),
                        new_tip='never',
                        blow_out=True
                        )
                else:
                    pipette.transfer(
                    	vol,
                    	source,
                    	dest,
                        new_tip='never',
                        blow_out=True
                        )
            pipette.drop_tip()

def distributeMixedInducer(pipette,mix_vol,vol,num_assay_plates,airgap_vol,source,dests):
    
    total_asp_vol = num_assay_plates * (airgap_vol + vol)
    
    if total_asp_vol >= pipette.max_volume:
        raise ValueError('Vol too large to handle in one aspiration')

    pipette.pick_up_tip()
    
    for x in range(3):
        pipette.aspirate(mix_vol,source)
        pipette.dispense(mix_vol,source)
        
    pipette.blow_out(source.top())

    pipette.air_gap(airgap_vol/2)
    for i in range(num_assay_plates):
        pipette.aspirate(vol,source)
        if i != num_assay_plates:
            pipette.air_gap(airgap_vol)
        else:
            pipette.air_gap(airgap_vol/2)
    
    dispense_vol = vol + airgap_vol
    for dest in dests:    
        pipette.dispense(dispense_vol,dest)
    pipette.drop_tip()

#%% 

# Plate tracking
        # Slot 10 = 300 uL tips
        # Slot 11 = 200 uL tips
        # Rack 2 = PCR plate for inducer aliquot
        # Rack 1 = inducer to place
        # Slots 4-6 = assay plates with LB loaded
        
slots_map = {
        #'1':'96-flat',
        '1':'opentrons-tuberack-2ml-eppendorf',
        '2':'96-flat',
        '3':'96-flat',
        '6':'96-deep-well'
        }

inducer_rack = '1'
#media_rack = '2'
#media_well = 'A3'
iap_x = '2'
iap_y = '3'
master_plate = '6'

inducer_y_map = {
        'A1':'A',
        'A2':'B',
        'A3':'C',
        'A4':'D',
        'A5':'E',
        'A6':'F',
        'B1':'G',
        'B2':'H'}
        

inducer_x_map = {'C1':'12',
                 'C2':'11',
                 'C3':'10',
                 'C4':'9',
                 'C5':'8',
                 'C6':'7',
                 'D1':'6',
                 'D2':'5',
                 'D3':'4',
                 'D4':'3',
                 'D5':'2',
                 'D6':'1'}


tip_slots1 = ['7']
tip_racks1 = [labware.load('tiprack-200ul', slot) for slot in tip_slots1]
tip_slots2 = ['10','11']
tip_racks2 = [labware.load('tiprack-10ul', slot) for slot in tip_slots2]


dead_vol = 6
num_assay_plates = 3.35
inducer_x_vol = 2
inducer_y_vol = 2
#media_vol = 16

assay_plates = ['4','5','6']

labware_items = {}
for slot, labware_item in slots_map.items():
    labware_items.update({slot:labware.load(labware_item, slot)})

p300s = instruments.P300_Single(
    mount='left',
    tip_racks=tip_racks1
    )

p10m = instruments.P10_Multi(
    mount='right',
    tip_racks=tip_racks2
    )

#%% Stage 1: Distribtue x axis gradient
    
ix_total = inducer_x_vol * num_assay_plates + dead_vol

for source_well, dest_col in inducer_x_map.items():
    distributeNoBlowOut(p300s,
                        ix_total,
                        labware_items[inducer_rack].wells(source_well),
                        labware_items[iap_x].cols(dest_col),
                        disposal_vol=3)
    # Add x axis inducers to deep-well plate
    p10m.transfer(
            inducer_x_vol * num_assay_plates,
            labware_items[iap_x].cols(dest_col),
            labware_items[master_plate].cols(dest_col).top(-30),
            blow_out=True,
            new_tip='always'                  
            )

#robot.pause()
#%% Stage 2: Distribute y axis gradient

# total vol of y axis inducer needed for each well in aliquot plate
iy_total = inducer_y_vol * 12 * num_assay_plates + dead_vol + 4

# Distribute the inducer for y axis
for source_well, dest_well in inducer_y_map.items():
    p300s.transfer(
        	iy_total,
        	labware_items[inducer_rack].wells(source_well),
        	labware_items[iap_y].cols('1').wells(dest_well),
            new_tip='always',
            blow_out=False
            )

# Add y axis inducers to deep-well plate
for col_index in range(12):
    p10m.transfer(
            inducer_x_vol * num_assay_plates,
            labware_items[iap_y].cols('1'),
            labware_items[master_plate].cols(col_index).top(-30),
            blow_out=True,
            new_tip='always'                  
            )
#%%
#for c in robot.commands():
#    print(c)
#
#robot.clear_commands()