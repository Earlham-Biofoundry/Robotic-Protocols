# -*- coding: utf-8 -*-
"""
Created on Wed Oct 22 16:31:16 2025

@author: yor25yat
"""

import json
from opentrons import protocol_api, types
import math
 
metadata = {
    "protocolName": "CG_sampleready_E.coli_transformation_run_parameters_V2",
    "created": "2025-10-22T14:33:46.712Z",
    "lastModified": "2025-10-22T15:08:48.431Z",
    "protocolDesigner": "8.5.6",
    "source": "OpentronsAI",
}
 
requirements = {"robotType": "Flex", "apiLevel": "2.24"}
 
def add_parameters(parameters):
    parameters.add_int(
        variable_name="number_of_samples",
        display_name="Number of Samples",
        description="Total number of samples to process (must be multiple of 8)",
        default=24,
        minimum=8,
        maximum=96,
        unit="samples"
    )
    parameters.add_int(
        variable_name="bacteria_volume",
        display_name="Comp. cells Volume (µL)",
        description="Volume of Comp. cells to transfer to wells",
        default=7,
        minimum=1,
        maximum=25,
        unit="µL"
    )

    parameters.add_int(
        variable_name="soc_volume",
        display_name="SOC Volume (µL)",
        description="Volume of SOC to transfer to destination plate",
        default=50,
        minimum=10,
        maximum=200,
        unit="µL"
    )

    parameters.add_str(
        variable_name="start_well_384",
        display_name="Start Well (384-well plate)",
        description="Starting well in the 384-well plate",
        default="A1",
        choices=[
            {"display_name": "A1", "value": "A1"},
            {"display_name": "B1", "value": "B1"},
            {"display_name": "A2", "value": "A2"},
            {"display_name": "B2", "value": "B2"},
            {"display_name": "A3", "value": "A3"},
            {"display_name": "B3", "value": "B3"},
            {"display_name": "A4", "value": "A4"},
            {"display_name": "B4", "value": "B4"},
            {"display_name": "A5", "value": "A5"},
            {"display_name": "B5", "value": "B5"},
            {"display_name": "A6", "value": "A6"},
            {"display_name": "B6", "value": "B6"},
            {"display_name": "A7", "value": "A7"},
            {"display_name": "B7", "value": "B7"},
            {"display_name": "A8", "value": "A8"},
            {"display_name": "B8", "value": "B8"},
            {"display_name": "A9", "value": "A9"},
            {"display_name": "B9", "value": "B9"},
            {"display_name": "A10", "value": "A10"},
            {"display_name": "B10", "value": "B10"},
            {"display_name": "A11", "value": "A11"},
            {"display_name": "B11", "value": "B11"},
            {"display_name": "A12", "value": "A12"},
            {"display_name": "B12", "value": "B12"}
        ]
    )

    parameters.add_int(
        variable_name="start_column_96",
        display_name="Start Column (96-well plate)",
        description="Starting column in the 96-well plate (1-12)",
        default=1,
        minimum=1,
        maximum=12,
        unit="column"
    )

def run(protocol: protocol_api.ProtocolContext) -> None:
    # Access runtime parameters
    bacteria_volume = protocol.params.bacteria_volume
    soc_volume = protocol.params.soc_volume
    number_of_samples = protocol.params.number_of_samples
    start_well_384 = protocol.params.start_well_384
    start_column_96 = protocol.params.start_column_96
    
    # Calculate number of columns needed (8 samples per column for 8-channel pipette)
    num_columns = math.ceil(number_of_samples / 8)
    
    # Calculate end column for 96-well plate
    end_column_96 = start_column_96 + num_columns - 1 #the minus one is because Python works with counting starting from 0.
    
    # Validate that we don't exceed plate boundaries
    if end_column_96 > 12:
        raise ValueError(f"Not enough columns in 96-well plate. Need {num_columns} columns starting from column {start_column_96}")
    
    # Parse starting well for 384-well plate to get row and column
    start_row_384 = start_well_384[0]
    start_col_384 = int(start_well_384[1:])
    
    # Calculate end column for 384-well plate
    end_col_384 = start_col_384 + num_columns - 1
    
    if end_col_384 > 24:
        raise ValueError(f"Not enough columns in 384-well plate. Need {num_columns} columns starting from column {start_col_384}")
    
    # Load Modules:
    temperature_module_1 = protocol.load_module("temperatureModuleV2", "B1")
 
    # Load Labware:
    tip_rack_1 = protocol.load_labware(
        "opentrons_flex_96_tiprack_50ul",
        location="A2",
        namespace="opentrons",
        version=1,
    )
    
    tip_rack_2 = protocol.load_labware(
        "opentrons_flex_96_tiprack_50ul",
        location="A1",
        namespace="opentrons",
        version=1,
    )
    tip_rack_3 = protocol.load_labware(
        "opentrons_flex_96_tiprack_200ul",
        location="A3",
        namespace="opentrons",
        version=1,
    )    
    reservoir_1 = protocol.load_labware(
        "nest_12_reservoir_22ml",
        location="B3",
        label="reservoir",
        namespace="opentrons",
        version=1,
    )
    aluminum_block_1 = temperature_module_1.load_labware(
        "opentrons_96_aluminumblock_generic_pcr_strip_200ul",
        namespace="opentrons",
        version=4,
    )
    _96_well_PCR = protocol.load_labware(
        "biorad_96_wellplate_200ul_pcr",
        location="C2",
        namespace="opentrons",
        version=3,
    )
    _384_well_plate = protocol.load_labware(
        "appliedbiosystemsmicroamp_384_wellplate_40ul",
        location="B2",
        namespace="opentrons",
        version=2,
    )
 

 
    # Load Pipettes:
    pipette_left = protocol.load_instrument(
        "flex_8channel_50", "left", tip_racks=[tip_rack_1, tip_rack_2],
    )
    pipette_right = protocol.load_instrument(
        "flex_8channel_1000", "right", tip_racks=[tip_rack_3],
    )
 
    # Load Waste Chute:
    waste_chute = protocol.load_waste_chute()
 
    # Define Liquids:
    liq_assembly = protocol.define_liquid(
        "Assembly",
        display_color="#ff4f4fff",
    )
    liq_SOC = protocol.define_liquid(
        "SOC",
        display_color="#ffd600ff",
    )
    liq_comp_cells = protocol.define_liquid(
        "comp cells",
        display_color="#ff9900ff",
    )
 
    # Load Liquids:
    aluminum_block_1.load_liquid(
        wells=[
            "A12", "B12", "C12", "D12", "E12", "F12", "G12", "H12"
        ],
        liquid=liq_comp_cells,
        volume=50,
    )
    
    # Generate destination wells for 384-well plate based on parameters
    # The 384-well plate follows an alternating A/B pattern within each column
    dest_wells_384 = []
    for col_offset in range(num_columns):
        col_num = start_col_384 + col_offset
        # Determine if we start with A or B row based on the starting well
        if start_row_384 == 'A':
            well_a = f"A{col_num}"
            well_b = f"B{col_num}"
            dest_wells_384.extend([_384_well_plate[well_a], _384_well_plate[well_b]])
        else:  # Starting with B
            well_b = f"B{col_num}"
            # Next well in pattern would be A of next column
            if col_num < 24:
                well_a_next = f"A{col_num + 1}"
                dest_wells_384.extend([_384_well_plate[well_b], _384_well_plate[well_a_next]])
            else:
                dest_wells_384.append(_384_well_plate[well_b])
    
    # Trim to exact number of columns needed
    dest_wells_384 = dest_wells_384[:num_columns]
    
    # Load liquid into calculated 384-well plate wells
    for well in dest_wells_384:
        well.load_liquid(liquid=liq_assembly, volume=5)
    
    reservoir_1.load_liquid(
        wells=["A1"],
        liquid=liq_SOC,
        volume=12000,
    )
    
    # Generate destination columns for 96-well plate based on parameters
    dest_columns_96 = []
    for col_offset in range(num_columns):
        col_num = start_column_96 + col_offset
        dest_columns_96.append(_96_well_PCR.columns()[col_num - 1][0])

    # PROTOCOL STEPS
    # Step 1: take temperature module to 4 degrees
    temperature_module_1.set_temperature(celsius=4)

    # Step 2: pause to put competent cells into temperature module. 
    protocol.pause("put Competent cells strip in Column 12. \n")

    # Step 3: Distribute bacteria (using runtime parameter)
    pipette_left.distribute_with_liquid_class(
        volume=bacteria_volume,
        source=[aluminum_block_1["A12"]],
        dest=dest_wells_384,
        new_tip="once",
        group_wells=False,
        trash_location=waste_chute,
        liquid_class=protocol.define_liquid_class(
            name="distribute_step_1",
            properties={"flex_8channel_50": {"opentrons/opentrons_flex_96_tiprack_50ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 0.2},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 24)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 100,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 50,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 1.2, "z": -3},
                        "position_reference": "well-top",
                    },
                    "flow_rate_by_volume": [(0, 50)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 100,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 50,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 2)],
                    "mix": {"enabled": False},
                },
                "multi_dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0.8, "z": -3},
                        "position_reference": "well-top",
                    },
                    "flow_rate_by_volume": [(0, 50)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 100,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 50,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "conditioning_by_volume": [(0, 0)],
                    "disposal_by_volume": [(0, 0)],
                },
            }}},
        ),
    )

    # Step 4:
    protocol.pause("Take the plate out AND PRESS RESUME to let the protocol pre-fill the destination plate with SOC.\n")

    # Step 5: Transfer SOC (using runtime parameter) to 96 well plate
    soc_sources = [reservoir_1["A1"]] * num_columns # Create source list (all from reservoir A1)

    pipette_right.transfer_with_liquid_class(
        volume=soc_volume,
        source=soc_sources,
        dest=dest_columns_96,
        new_tip="once",
        trash_location=waste_chute,
        group_wells=False,
        keep_last_tip=False,
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_3",
            properties={"flex_8channel_1000": {"opentrons/opentrons_flex_96_tiprack_200ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 1},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 716)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 100,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 50,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 0},
                        "position_reference": "well-center",
                    },
                    "flow_rate_by_volume": [(0, 716)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 100,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 50,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 20)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )

    # Step 6:
    protocol.pause("Put the plate back into B2")

    # Step 7: Transfer SOC to Assembly plate (using runtime parameter) then mix and transfer the diluted bact into 96 well plate. 
    for x in range(num_columns):
        pipette_left.transfer_with_liquid_class(
            volume=10,
            source=soc_sources[x],
            dest=dest_wells_384[x],
            new_tip="always",
            group_wells = False,
            keep_last_tip = True,
            liquid_class=protocol.define_liquid_class(
                name="add SOC to 384 well plate",
                properties={"flex_8channel_50": {"opentrons/opentrons_flex_96_tiprack_50ul/1": {
                    "aspirate": {
                        "aspirate_position": {
                            "offset": {"x": 0, "y": 0, "z": 1},
                            "position_reference": "well-bottom",
                            },
                        "flow_rate_by_volume": [(0, 24)],
                        "pre_wet": False,
                        "correction_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "mix": {"enabled": False},
                        "submerge": {
                            "delay": {"enabled": False},
                            "speed": 100,
                            "start_position": {
                                "offset": {"x": 0, "y": 0, "z": 2},
                                "position_reference": "well-top",
                                },
                            },
                        "retract": {
                            "air_gap_by_volume": [(0, 0)],
                            "delay": {"enabled": False},
                            "end_position": {
                                "offset": {"x": 0, "y": 0, "z": 2},
                                "position_reference": "well-top",
                                },
                            "speed": 50,
                            "touch_tip": {"enabled": False},
                            },
                        },
                    "dispense": {
                        "dispense_position": {
                            "offset": {"x": 0, "y": 0, "z": 1},
                            "position_reference": "well-bottom",
                            },
                        "flow_rate_by_volume": [(0, 50)],
                        "delay": {"enabled": False},
                        "submerge": {
                            "delay": {"enabled": False},
                            "speed": 100,
                            "start_position": {
                                "offset": {"x": 0, "y": 0, "z": 2},
                                "position_reference": "well-top",
                                },
                            },
                        "retract": {
                            "air_gap_by_volume": [(0, 0)],
                            "delay": {"enabled": False},
                            "end_position": {
                                "offset": {"x": 0, "y": 0, "z": 0},
                                "position_reference": "well-top",
                                },
                            "speed": 50,
                            "touch_tip": {"enabled": False},
                            "blowout": {"enabled": False},
                        },
                        "correction_by_volume": [(0, 0)],
                        "push_out_by_volume": [(0, 2)],
                        "mix": {"enabled": False},
                    },
                }}},
            ),
        )
        pipette_left.transfer_with_liquid_class(
            volume=40,
            source=dest_wells_384[x],
            dest=dest_columns_96[x],
            new_tip="never",
            trash_location=waste_chute,
            group_wells=False,
            keep_last_tip=False,
            liquid_class=protocol.define_liquid_class(
                name="transfer_step_6",
                properties={"flex_8channel_50": {"opentrons/opentrons_flex_96_tiprack_50ul/1": {
                    "aspirate": {
                        "aspirate_position": {
                            "offset": {"x": 0, "y": 0, "z": 0.6},
                            "position_reference": "well-bottom",
                        },
                        "flow_rate_by_volume": [(0, 29.5)],
                        "pre_wet": False,
                        "correction_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "mix": {"enabled": True, "repetitions": 3, "volume": 20},
                        "submerge": {
                            "delay": {"enabled": False},
                            "speed": 100,
                            "start_position": {
                                "offset": {"x": 0, "y": 0, "z": 2},
                                "position_reference": "well-top",
                            },
                        },
                        "retract": {
                            "air_gap_by_volume": [(0, 0)],
                            "delay": {"enabled": False},
                            "end_position": {
                                "offset": {"x": 0, "y": 0, "z": 2},
                                "position_reference": "well-top",
                            },
                            "speed": 50,
                            "touch_tip": {"enabled": False},
                        },
                    },
                    "dispense": {
                        "dispense_position": {
                            "offset": {"x": 0, "y": 0, "z": 3},
                            "position_reference": "well-bottom",
                        },
                        "flow_rate_by_volume": [(0, 50)],
                        "delay": {"enabled": False},
                        "submerge": {
                            "delay": {"enabled": False},
                            "speed": 100,
                            "start_position": {
                                "offset": {"x": 0, "y": 0, "z": 0},
                                "position_reference": "well-top",
                            },
                        },
                        "retract": {
                            "air_gap_by_volume": [(0, 0)],
                            "delay": {"enabled": False},
                            "end_position": {
                                "offset": {"x": 0, "y": 0, "z": 2},
                                "position_reference": "well-top",
                            },
                            "speed": 50,
                            "touch_tip": {"enabled": False},
                            "blowout": {"enabled": False},
                        },
                        "correction_by_volume": [(0, 0)],
                        "push_out_by_volume": [(0, 2)],
                        "mix": {"enabled": True, "repetitions": 4, "volume": ((soc_volume+bacteria_volume+10+20)/2)},
                    },
                }}},
            ),
        )
