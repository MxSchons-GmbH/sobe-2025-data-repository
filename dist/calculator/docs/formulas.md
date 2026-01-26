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

## Recording Formulas

### Recording

| ID | Formula | Unit | Description |
|----|---------|------|-------------|
| `recording_experiment_duration_seconds` | `experiment_length * 3600` | seconds | Experiment duration in seconds |
| `recording_samples_per_experiment` | `floor(recording_experiment_duration_seconds / sample_duration)` | count | Number of samples per experiment given user-defined sample duration |
| `recording_brain_volume_to_record` | `biological_volume * brain_volume_coverage` | mm³ | Brain volume to record based on user-defined coverage percentage |
| `recording_experiments_for_volume_coverage` | `ceil(recording_brain_volume_to_record / experiment_brain_volume)` | count | Experiments needed for brain volume coverage (assuming non-overlapping) |
| `recording_total_experiments` | `recording_experiments_for_volume_coverage * brain_area_repetitions` | count | Total experiments accounting for repeated scans of same area (e.g., different brain states) |
| `recording_samples_per_brain_area` | `recording_samples_per_experiment * brain_area_repetitions` | count | Average samples per brain volume area |
| `recording_total_samples` | `recording_total_experiments * recording_samples_per_experiment` | count | Total samples across all experiments |
| `recording_total_data_volume_tb` | `recording_total_experiments * experiment_data_volume` | TB | Total uncompressed data volume in TB |
| `recording_total_data_volume_pb` | `recording_total_data_volume_tb / 1000` | PB | Total uncompressed data volume in PB |
| `recording_neurons_covered` | `min(recording_total_experiments * neurons_at_single_resolution, neuron_count * brain_volume_coverage)` | count | Total neurons covered by recordings |
| `recording_coverage_percent` | `(recording_neurons_covered / neuron_count) * 100` | % | Percentage of brain neurons covered |
| `recording_total_experiment_cost` | `recording_total_experiments * experiment_cost` | $ | Total experiment costs (excluding storage) |
| `recording_connectomics_volume` | `recording_brain_volume_to_record * connectomics_scan_percentage` | mm³ | Brain volume for aligned structural/functional datasets |
| `recording_total_recording_hours` | `recording_total_experiments * experiment_length` | hours | Total recording time |
| `recording_infrastructure_cost_first` | `500000` | $ | Equipment setup cost (fixed) |
| `recording_personnel_cost_first` | `5 * 150000 * min(recording_total_recording_hours / (24 * 365), 3)` | $ | Personnel cost for team (up to 3 years) |
| `recording_total_cost_first` | `(recording_total_experiment_cost + recording_infrastructure_cost_first + recording_personnel_cost_first) * (1 + risk_buffer_first)` | $ | Total first project cost with buffer |
| `recording_total_time_years_first` | `(recording_total_recording_hours / (24 * 365)) * (1 + risk_buffer_first)` | years | Total first project time with buffer |
| `recording_marginal_experiment_cost` | `experiment_cost * 0.8` | $ | Marginal cost per experiment (80% of first) |
| `recording_total_cost_marginal` | `(recording_total_experiments * recording_marginal_experiment_cost) * (1 + risk_buffer_marginal)` | $ | Total marginal project cost |
| `recording_total_time_years_marginal` | `(recording_total_recording_hours * 0.7 / (24 * 365)) * (1 + risk_buffer_marginal)` | years | Total marginal project time (30% faster) |

## Simulation Formulas

### Simulation

| ID | Formula | Unit | Description |
|----|---------|------|-------------|
| `simulation_total_memory_bytes` | `storage_bytes_lower` | bytes | Total memory footprint (using lower bound) |
| `simulation_total_memory_gb` | `simulation_total_memory_bytes / 1e9` | GB | Total memory in gigabytes |
| `simulation_flops_per_sec` | `flops_time_based_lower` | FLOPS | FLOPS required per second (time-based, lower bound) |
| `simulation_gpus_for_memory` | `ceil(simulation_total_memory_gb / gpu_memory_gb)` | count | GPUs needed for memory |
| `simulation_gpus_for_compute` | `ceil(simulation_flops_per_sec / (gpu_tflops * 1e12))` | count | GPUs needed for compute |
| `simulation_total_gpus` | `max(simulation_gpus_for_memory, simulation_gpus_for_compute)` | count | Total GPUs required |
| `simulation_runtime_cost` | `simulation_total_gpus * gpu_cost_per_hour * simulation_hours` | $ | Simulation runtime cost |
| `simulation_training_infrastructure_cost` | `10000000` | $ | Training infrastructure cost (fixed) |
| `simulation_training_compute_cost` | `simulation_runtime_cost * 0.1` | $ | Training compute cost (10% of simulation) |
| `simulation_validation_cost` | `simulation_runtime_cost * 0.05` | $ | Validation cost (5% of simulation) |
| `simulation_total_cost_first` | `(simulation_runtime_cost + simulation_training_infrastructure_cost + simulation_training_compute_cost + simulation_validation_cost) * 1.2` | $ | Total first project cost with 20% buffer |
| `simulation_total_time_years_first` | `(simulation_hours / (24 * 365)) * 1.2` | years | Total first project time with buffer |
| `simulation_retraining_cost` | `simulation_training_compute_cost * 0.1` | $ | Marginal retraining cost (10%) |
| `simulation_finetuning_cost` | `simulation_validation_cost * 0.02` | $ | Marginal finetuning cost (2%) |
| `simulation_total_cost_marginal` | `simulation_runtime_cost + simulation_retraining_cost + simulation_finetuning_cost` | $ | Total marginal project cost |
| `simulation_total_time_years_marginal` | `simulation_hours / (24 * 365)` | years | Total marginal project time |

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
- **recording_experiment_duration_seconds** depends on: `experiment_length`
- **recording_samples_per_experiment** depends on: `recording_experiment_duration_seconds`, `sample_duration`
- **recording_brain_volume_to_record** depends on: `biological_volume`, `brain_volume_coverage`
- **recording_experiments_for_volume_coverage** depends on: `recording_brain_volume_to_record`, `experiment_brain_volume`
- **recording_total_experiments** depends on: `recording_experiments_for_volume_coverage`, `brain_area_repetitions`
- **recording_samples_per_brain_area** depends on: `recording_samples_per_experiment`, `brain_area_repetitions`
- **recording_total_samples** depends on: `recording_total_experiments`, `recording_samples_per_experiment`
- **recording_total_data_volume_tb** depends on: `recording_total_experiments`, `experiment_data_volume`
- **recording_total_data_volume_pb** depends on: `recording_total_data_volume_tb`
- **recording_neurons_covered** depends on: `recording_total_experiments`, `neurons_at_single_resolution`, `neuron_count`, `brain_volume_coverage`
- **recording_coverage_percent** depends on: `recording_neurons_covered`, `neuron_count`
- **recording_total_experiment_cost** depends on: `recording_total_experiments`, `experiment_cost`
- **recording_connectomics_volume** depends on: `recording_brain_volume_to_record`, `connectomics_scan_percentage`
- **recording_total_recording_hours** depends on: `recording_total_experiments`, `experiment_length`
- **recording_personnel_cost_first** depends on: `recording_total_recording_hours`
- **recording_total_cost_first** depends on: `recording_total_experiment_cost`, `recording_infrastructure_cost_first`, `recording_personnel_cost_first`, `risk_buffer_first`
- **recording_total_time_years_first** depends on: `recording_total_recording_hours`, `risk_buffer_first`
- **recording_marginal_experiment_cost** depends on: `experiment_cost`
- **recording_total_cost_marginal** depends on: `recording_total_experiments`, `recording_marginal_experiment_cost`, `risk_buffer_marginal`
- **recording_total_time_years_marginal** depends on: `recording_total_recording_hours`, `risk_buffer_marginal`
- **simulation_total_memory_bytes** depends on: `storage_bytes_lower`
- **simulation_total_memory_gb** depends on: `simulation_total_memory_bytes`
- **simulation_flops_per_sec** depends on: `flops_time_based_lower`
- **simulation_gpus_for_memory** depends on: `simulation_total_memory_gb`, `gpu_memory_gb`
- **simulation_gpus_for_compute** depends on: `simulation_flops_per_sec`, `gpu_tflops`
- **simulation_total_gpus** depends on: `simulation_gpus_for_memory`, `simulation_gpus_for_compute`
- **simulation_runtime_cost** depends on: `simulation_total_gpus`, `gpu_cost_per_hour`, `simulation_hours`
- **simulation_training_compute_cost** depends on: `simulation_runtime_cost`
- **simulation_validation_cost** depends on: `simulation_runtime_cost`
- **simulation_total_cost_first** depends on: `simulation_runtime_cost`, `simulation_training_infrastructure_cost`, `simulation_training_compute_cost`, `simulation_validation_cost`
- **simulation_total_time_years_first** depends on: `simulation_hours`
- **simulation_retraining_cost** depends on: `simulation_training_compute_cost`
- **simulation_finetuning_cost** depends on: `simulation_validation_cost`
- **simulation_total_cost_marginal** depends on: `simulation_runtime_cost`, `simulation_retraining_cost`, `simulation_finetuning_cost`
- **simulation_total_time_years_marginal** depends on: `simulation_hours`
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
