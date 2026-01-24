# Parameter Reference

This document describes all input parameters used in the brain emulation calculator.
These values can be edited in the TSV files under `data/parameters/`.

---

## Shared Parameters

Project-level parameters that apply across all calculations.

| Parameter | Value | Unit | Description |
|-----------|-------|------|-------------|
| Volume (biological) | undefined | mm³ | Physical brain volume to be mapped |
| Number of neurons | undefined | count | Number of neurons in the given volume |
| Risk buffer first connectome | undefined | fraction | Budget and schedule contingency fraction |
| Risk buffer marginal connectomes | undefined | fraction | Budget and schedule contingency fraction |
| Years until start | undefined | years | Years from now when initial purchases are made |
| Project duration | undefined | years | Time span for overall project |
| Microscope budget | undefined | $ | Upfront investment in microscopes |
| Max parallel GPUs | undefined | count | Number of GPUs dedicated during processing |
| Facility per year | undefined | $/year | Cleanroom, isolation, HVAC, racks |
| Average staff salary | undefined | $/year | Average salary with all overheads |
| Project management staff | undefined | FTE | Staff for project oversight |
| Technical staff | undefined | FTE | Beyond sample and microscope operations |
| Misc staff | undefined | FTE | Operations, assistants, PR, etc |
| Other costs per connectome | undefined | $ | Shipping, permits, biosafety, IP, pubs |
| Data science development | undefined | $ | Pipelines, data mgmt, viewers, model training |
| Capital base | undefined | $ | Scopes + facility + core SW + initial training |
| Peak FLOPs/s GPU | undefined | TFLOPs/s | Maximum FP16 FLOP/s for GPU |
| GPU utilization | undefined | fraction | Continuous GPU usage across time |
| GPU cost per hour | undefined | $/hour | Costs for access to 1h of GPU |
| Cost drop compute/year | undefined | fraction | Cost drop compute per year |
| Cost drop storage/year | undefined | fraction | Cost drop storage per year |
| Active storage cost | undefined | $/PB-month | Storage for working files |
| Archive storage cost | undefined | $/PB-month | Storage for backup files |
| Bytes per voxel | undefined | bytes | Assuming 8-bits per voxel |
| Lossless compression | undefined | × | Raw to lossless ratio |
| Lossy compression | undefined | × | Raw to lossy ratio |
| Label overhead | undefined | fraction | Labels + meshes + skeletons + graphs |
| Replicas active (first) | undefined | count | Hot copies lossless online first |
| Replicas archive (first) | undefined | count | Cold copies retained first |
| Replicas active (marginal) | undefined | count | Hot copies lossless online marginal |
| Replicas archive (marginal) | undefined | count | Cold copies retained marginal |
| Active retention | undefined | years | How long active copies are kept |
| Archive retention | undefined | years | How long archive copies are kept |
| Active storage cost/PB-year | undefined | $/PB-year | Online storage price |
| Archive storage cost/PB-year | undefined | $/PB-year | Archive storage price |
| FLOPs registration/tile | undefined | TFLOP/tile | FP32-equivalent per tile |
| Segmentation FLOPs/voxel | undefined | TFLOP/voxel | FP32-equivalent per voxel |
| Registration rate | undefined | PV/day/GPU | PV processed per day per GPU |
| Segmentation rate | undefined | PV/day/GPU | PV processed per day per GPU |

## Imaging Modalities

Parameters specific to each imaging technology.

| Parameter | Unit | EM | EXM | EXM_MOLECULAR | WELLCOME |
|-----------|------|---|---|---|---|
| Microscope capital cost | $/scope | 500.0K | 500.0K | 500.0K | 5.0M |
| Depreciation horizon | years | 10 | 5 | 5 | 10 |
| Sustained imaging rate | Mvox/s | 225 | 1.1K | 1.1K | 250 |
| Parallel channels | count | 1 | 3 | 8 | 1 |
| Total channels | count | 1 | 1 | 800 | 1 |
| Annual service | $/scope/year | 50.0K | 15.0K | 15.0K | 250.0K |
| Technician salary | $/year | 120.0K | 120.0K | 120.0K | 120.0K |
| Technician ratio | count | 2 | 5 | 5 | 0.50 |
| Microscope uptime | fraction | 1 | 1 | 1 | 1 |
| Reacquisition rate | fraction | 0 | 0 | 0 | 0 |
| Sample yield | fraction | 1 | 1 | 1 | 1 |
| Expansion factor | × | 1 | 16 | 16 | 1 |
| Consumables per mm³ | $/mm³ | 100.0K | 2 | 2 | 200.0K |
| Antibody cost per mm³ | $/mm³ | 2 | 2 | 2 | 2 |
| Labor cost per mm³ | $/mm³ | 2.9K | 2.9K | 2.9K | 2.9K |
| Initial preparation days | days | 15 | 15 | 15 | 15 |
| Voxel size X | nm | 15 | 250 | 250 | 10 |
| Voxel size Y | nm | 15 | 250 | 250 | 10 |
| Voxel size Z | nm | 15 | 400 | 400 | 10 |
| Sample depth | count | 1 | 10.0K | 10.0K | 1 |
| Tile overlap | fraction | 0.10 | 0.10 | 0.10 | 0.10 |

## Organisms

Reference data for different model organisms.

| Organism | Neurons | Volume (mm³) | Synapses | Source |
|----------|---------|--------------|----------|--------|
| C. elegans | 302 | 0.00 | 7.5K | WormAtlas |
| Drosophila (fruit fly) | 135.0K | 0.50 | 50.0M | FlyWire |
| Zebrafish larva | 100.0K | 0.10 | 10.0M | Literature |
| Mouse | 70.0M | 500 | 700.0B | Literature |
| Macaque | 6.4B | 87.0K | 64.0T | Literature |
| Human | 86.0B | 1.2M | 150.0T | Literature |

## Proofreading Parameters

Human proofreading assumptions for different technology scenarios.

| Parameter | Unit | Current | 1000× Improved |
|-----------|------|---------|----------------|
| Human proofreading hours per neuron | hours | 5 | NaN |
| Hourly rate of proof-reader | $/hour | 50 | NaN |
| Proofreading hours per day | hours/day | 6 | NaN |
| Number of proofreaders | count | 25.0K | NaN |

