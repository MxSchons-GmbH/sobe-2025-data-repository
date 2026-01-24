# Formula Reference

This document describes all calculation formulas used in the brain emulation calculator.
Formulas are defined in TSV files under `data/formulas/` and evaluated using [mathjs](https://mathjs.org/).

---

## Connectomics Formulas

### Imaging

| ID | Formula | Unit | Description |
|----|---------|------|-------------|
| `voxels_per_mm3` | `1e18 / (voxel_x * voxel_y * voxel_z)` | voxels/mm³ | Number of voxels in one cubic millimeter at acquisition resolution |
| `effective_volume` | `biological_volume * expansion_factor^3 * (1 + reacquisition_rate)` | mm³ | Total volume to image after tissue expansion |
| `petavoxels_per_mm3` | `voxels_per_mm3 / 1e15` | PV/mm³ | Petavoxels per cubic millimeter |
| `petavoxels_total` | `petavoxels_per_mm3 * effective_volume` | PV | Total petavoxels to image |
| `net_imaging_rate` | `sustained_imaging_rate / (total_channels / parallel_channels) * microscope_uptime` | Mvox/s | Effective imaging speed accounting for channel rounds and uptime |
| `mm3_per_day_per_scope` | `(net_imaging_rate * 1e6 * 86400) / voxels_per_mm3` | mm³/day | Volume one microscope can image per day |
| `num_microscopes` | `floor(microscope_budget / microscope_capital_cost)` | count | Number of microscopes affordable within budget |
| `scope_operating_cost_per_year` | `technician_salary / microscope_technician_ratio + scope_annual_service` | $/year | Annual operating cost per microscope |

### Timeline

| ID | Formula | Unit | Description |
|----|---------|------|-------------|
| `imaging_days` | `if(mm3_per_day_per_scope * num_microscopes == 0, 0, effective_volume / (mm3_per_day_per_scope * num_microscopes) + initial_prep_days)` | days | Total days to complete all imaging |
| `imaging_years` | `imaging_days / 365` | years | Imaging time in years |
| `registration_days` | `biological_volume / (registration_rate_pv_per_day * max_parallel_gpus)` | days | Days for image registration/alignment |
| `segmentation_days` | `biological_volume / (segmentation_rate_pv_per_day * max_parallel_gpus)` | days | Days for neural segmentation |
| `processing_days` | `registration_days + segmentation_days` | days | Total GPU processing time |
| `processing_years` | `processing_days / 365` | years | Processing time in years |
| `proofreading_days` | `neuron_count * hours_per_neuron / (num_proofreaders * hours_per_day)` | days | Total human proofreading time |
| `proofreading_years` | `proofreading_days / 365` | years | Proofreading time in years |
| `buffer_years` | `(imaging_years + processing_years + proofreading_years) * risk_buffer_first` | years | Risk buffer time for first connectome |
| `time_to_first_years` | `imaging_years + processing_years + proofreading_years + buffer_years` | years | Total years until first connectome complete |
| `time_to_marginal_years` | `max(imaging_years, processing_years, proofreading_years)` | years | Years between subsequent connectomes (bottleneck) |

### Summary

| ID | Formula | Unit | Description |
|----|---------|------|-------------|
| `total_connectomes` | `round(project_duration / max(time_to_first_years, time_to_marginal_years))` | count | Number of connectomes achievable in project duration |

## Costs Formulas

### Costs

| ID | Formula | Unit | Description |
|----|---------|------|-------------|
| `consumables_cost` | `biological_volume * (consumables_per_mm3 + labor_cost_per_mm3 + antibody_cost_per_mm3 * (total_channels - 1))` | $ | Sample preparation and consumables cost |
| `scanning_cost` | `scope_operating_cost_per_year * num_microscopes * imaging_years` | $ | Microscope operating costs during imaging |
| `imaging_cost_total` | `consumables_cost + scanning_cost` | $ | Total imaging costs |
| `processing_cost_registration` | `max_parallel_gpus * registration_days * 24 * gpu_cost_per_hour / biological_volume` | $/PV | Registration compute cost per petavoxel |
| `processing_cost_segmentation` | `max_parallel_gpus * segmentation_days * gpu_cost_per_hour * 24 / petavoxels_total` | $/PV | Segmentation compute cost per petavoxel |
| `processing_cost_total` | `petavoxels_total * (processing_cost_registration + processing_cost_segmentation)` | $ | Total processing compute cost |
| `proofreading_cost` | `neuron_count * hours_per_neuron * hourly_rate` | $ | Total proofreading labor cost |
| `personnel_cost` | `(project_mgmt_staff + technical_staff + misc_staff) * avg_staff_salary * project_duration / total_connectomes` | $ | Personnel costs per connectome |
| `other_costs` | `other_costs_per_connectome` | $ | Miscellaneous costs (shipping, permits, etc.) |
| `first_subtotal` | `imaging_cost_total + total_storage_cost_first + processing_cost_total + proofreading_cost + personnel_cost + other_costs + data_science_cost + capital_base` | $ | First connectome costs before buffer |
| `first_buffer` | `first_subtotal * risk_buffer_first` | $ | Risk buffer for first connectome |
| `first_total` | `first_subtotal + first_buffer` | $ | Total cost for first connectome |
| `first_cost_per_neuron` | `first_total / neuron_count` | $/neuron | First connectome cost per neuron |
| `marginal_subtotal` | `imaging_cost_total + total_storage_cost_marginal + processing_cost_total + proofreading_cost + personnel_cost + other_costs` | $ | Marginal connectome costs before buffer |
| `marginal_buffer` | `marginal_subtotal * risk_buffer_marginal` | $ | Risk buffer for marginal connectomes |
| `marginal_total` | `marginal_subtotal + marginal_buffer` | $ | Total cost for marginal connectome |
| `marginal_cost_per_neuron` | `marginal_total / neuron_count` | $/neuron | Marginal connectome cost per neuron |
| `avg_total` | `if(total_connectomes > 1, (first_total + marginal_total * (total_connectomes - 1)) / total_connectomes, first_total)` | $ | Average cost per connectome |
| `avg_cost_per_neuron` | `if(total_connectomes > 1, (first_cost_per_neuron + marginal_cost_per_neuron * (total_connectomes - 1)) / total_connectomes, first_cost_per_neuron)` | $/neuron | Average cost per neuron across all connectomes |

## Storage Formulas

### Storage

| ID | Formula | Unit | Description |
|----|---------|------|-------------|
| `raw_bytes_per_mm3` | `voxels_per_mm3 * bytes_per_voxel` | bytes/mm³ | Uncompressed bytes per cubic millimeter |
| `raw_pb_total` | `raw_bytes_per_mm3 * effective_volume / 1e15` | PB | Total raw uncompressed data size |
| `active_pb` | `if(lossy_compression == 0, 0, (raw_pb_total / lossy_compression) + (raw_pb_total * label_overhead))` | PB | Active storage size (lossy compressed + labels) |
| `archive_pb` | `if(lossless_compression == 0, 0, (raw_pb_total / lossless_compression) + (raw_pb_total * label_overhead))` | PB | Archive storage size (lossless compressed + labels) |
| `active_storage_cost_first` | `active_pb * replicas_active_first * active_retention_years * active_cost_pb_year` | $ | Active storage cost for first connectome |
| `archive_storage_cost_first` | `archive_pb * replicas_archive_first * archive_retention_years * archive_cost_pb_year` | $ | Archive storage cost for first connectome |
| `total_storage_cost_first` | `active_storage_cost_first + archive_storage_cost_first` | $ | Total storage cost for first connectome |
| `active_storage_cost_marginal` | `active_pb * replicas_active_marginal * active_retention_years * active_cost_pb_year` | $ | Active storage cost for marginal connectomes |
| `archive_storage_cost_marginal` | `archive_pb * replicas_archive_marginal * archive_retention_years * archive_cost_pb_year` | $ | Archive storage cost for marginal connectomes |
| `total_storage_cost_marginal` | `active_storage_cost_marginal + archive_storage_cost_marginal` | $ | Total storage cost for marginal connectomes |

## Formula Dependencies

Each formula depends on input parameters and/or other formulas. The calculator
automatically resolves these dependencies in the correct order.

- **voxels_per_mm3** depends on: `voxel_x`, `voxel_y`, `voxel_z`
- **effective_volume** depends on: `biological_volume`, `expansion_factor`, `reacquisition_rate`
- **petavoxels_per_mm3** depends on: `voxels_per_mm3`
- **petavoxels_total** depends on: `petavoxels_per_mm3`, `effective_volume`
- **net_imaging_rate** depends on: `sustained_imaging_rate`, `total_channels`, `parallel_channels`, `microscope_uptime`
- **mm3_per_day_per_scope** depends on: `net_imaging_rate`, `voxels_per_mm3`
- **num_microscopes** depends on: `microscope_budget`, `microscope_capital_cost`
- **scope_operating_cost_per_year** depends on: `technician_salary`, `microscope_technician_ratio`, `scope_annual_service`
- **imaging_days** depends on: `effective_volume`, `mm3_per_day_per_scope`, `num_microscopes`, `initial_prep_days`
- **imaging_years** depends on: `imaging_days`
- **registration_days** depends on: `biological_volume`, `registration_rate_pv_per_day`, `max_parallel_gpus`
- **segmentation_days** depends on: `biological_volume`, `segmentation_rate_pv_per_day`, `max_parallel_gpus`
- **processing_days** depends on: `registration_days`, `segmentation_days`
- **processing_years** depends on: `processing_days`
- **proofreading_days** depends on: `neuron_count`, `hours_per_neuron`, `num_proofreaders`, `hours_per_day`
- **proofreading_years** depends on: `proofreading_days`
- **buffer_years** depends on: `imaging_years`, `processing_years`, `proofreading_years`, `risk_buffer_first`
- **time_to_first_years** depends on: `imaging_years`, `processing_years`, `proofreading_years`, `buffer_years`
- **time_to_marginal_years** depends on: `imaging_years`, `processing_years`, `proofreading_years`
- **total_connectomes** depends on: `project_duration`, `time_to_first_years`, `time_to_marginal_years`
- **consumables_cost** depends on: `biological_volume`, `consumables_per_mm3`, `labor_cost_per_mm3`, `antibody_cost_per_mm3`, `total_channels`
- **scanning_cost** depends on: `scope_operating_cost_per_year`, `num_microscopes`, `imaging_years`
- **imaging_cost_total** depends on: `consumables_cost`, `scanning_cost`
- **processing_cost_registration** depends on: `max_parallel_gpus`, `registration_days`, `gpu_cost_per_hour`, `biological_volume`
- **processing_cost_segmentation** depends on: `max_parallel_gpus`, `segmentation_days`, `gpu_cost_per_hour`, `petavoxels_total`
- **processing_cost_total** depends on: `petavoxels_total`, `processing_cost_registration`, `processing_cost_segmentation`
- **proofreading_cost** depends on: `neuron_count`, `hours_per_neuron`, `hourly_rate`
- **personnel_cost** depends on: `project_mgmt_staff`, `technical_staff`, `misc_staff`, `avg_staff_salary`, `project_duration`, `total_connectomes`
- **other_costs** depends on: `other_costs_per_connectome`
- **first_subtotal** depends on: `imaging_cost_total`, `total_storage_cost_first`, `processing_cost_total`, `proofreading_cost`, `personnel_cost`, `other_costs`, `data_science_cost`, `capital_base`
- **first_buffer** depends on: `first_subtotal`, `risk_buffer_first`
- **first_total** depends on: `first_subtotal`, `first_buffer`
- **first_cost_per_neuron** depends on: `first_total`, `neuron_count`
- **marginal_subtotal** depends on: `imaging_cost_total`, `total_storage_cost_marginal`, `processing_cost_total`, `proofreading_cost`, `personnel_cost`, `other_costs`
- **marginal_buffer** depends on: `marginal_subtotal`, `risk_buffer_marginal`
- **marginal_total** depends on: `marginal_subtotal`, `marginal_buffer`
- **marginal_cost_per_neuron** depends on: `marginal_total`, `neuron_count`
- **avg_total** depends on: `total_connectomes`, `first_total`, `marginal_total`
- **avg_cost_per_neuron** depends on: `total_connectomes`, `first_cost_per_neuron`, `marginal_cost_per_neuron`
- **raw_bytes_per_mm3** depends on: `voxels_per_mm3`, `bytes_per_voxel`
- **raw_pb_total** depends on: `raw_bytes_per_mm3`, `effective_volume`
- **active_pb** depends on: `raw_pb_total`, `lossy_compression`, `label_overhead`
- **archive_pb** depends on: `raw_pb_total`, `lossless_compression`, `label_overhead`
- **active_storage_cost_first** depends on: `active_pb`, `replicas_active_first`, `active_retention_years`, `active_cost_pb_year`
- **archive_storage_cost_first** depends on: `archive_pb`, `replicas_archive_first`, `archive_retention_years`, `archive_cost_pb_year`
- **total_storage_cost_first** depends on: `active_storage_cost_first`, `archive_storage_cost_first`
- **active_storage_cost_marginal** depends on: `active_pb`, `replicas_active_marginal`, `active_retention_years`, `active_cost_pb_year`
- **archive_storage_cost_marginal** depends on: `archive_pb`, `replicas_archive_marginal`, `archive_retention_years`, `archive_cost_pb_year`
- **total_storage_cost_marginal** depends on: `active_storage_cost_marginal`, `archive_storage_cost_marginal`
