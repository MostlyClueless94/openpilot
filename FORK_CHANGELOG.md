# MostlyClueless94 SunnyPilot Subaru Fork Changelog

This file tracks all custom fork changes for Subaru angle-LKAS support and related fixes.

## Active Install URLs

- Stable: `https://installer.comma.ai/MostlyClueless94/master`
- Testing: `https://installer.comma.ai/MostlyClueless94/MostlyClueless`

## Branch Policy

- `master`: primary stable/public install branch.
- `MostlyClueless`: personal testing branch before promoting changes to `master`.
- Only `master` and `MostlyClueless` should be used as install branches.
- Do not use `-tici` branches on comma four.

## Current Commit Map (2026-03-17)

### Superproject (`MostlyClueless94/sunnypilot`)

- `master` -> `ca32db6c5eb8799d2d2c04d029afc181e5e6e897`
- `MostlyClueless` -> `7498ce404745e3a4acb49dab8498e9813a8eaf91`

### Submodule (`opendbc_repo`)

- `master` pointer: `c527da39a561f598f744e6acce4133d00f346bf3` (`opendbc-master-low-speed-smooth`)
- `MostlyClueless` pointer: `2b55f05633e0f6662e2776494e643da96b384486` (`opendbc-mostlyclueless`)
- Reference tag for pre-mitigation state: `5e57cb77dd1ec5843bcf841ff465b2fa3ece9632` (`opendbc-master-submodule`)

## Changelog

### 2026-03-18

- Branches updated: `master`.
- Submodule commit(s): `b9f363c84` - `subaru: yield mads angle control during manual steering`
- Why changed: promote the Subaru MADS manual-steer yield behavior from `MostlyClueless` to `master` so tight manual turns no longer fight the driver during MADS-only lateral use.
- Scope: lateral-only Subaru angle control; no longitudinal changes and no change to full engaged lateral behavior.
- Validation done: `python -m py_compile opendbc_repo/opendbc/car/subaru/carcontroller.py`.
- Known risks: still needs in-car confirmation for steering feel and smooth resume after the driver releases the wheel.

### 2026-03-17 (Branch Surface Reset)

#### Branch target

- `master` stable lane + shared public guidance

#### What changed

- Renamed the personal testing branch from `alpha` to `MostlyClueless`.
- Reduced the public branch surface to a strict two-lane workflow.
- Removed the extra public testing variants that were no longer part of the intended install flow.
- Updated install guidance:
  - stable installs should use `master`
  - personal testing installs should use `MostlyClueless`
  - no `-tici` branch should be used for comma four

#### Validation done

- Confirmed the stable lane remains on `opendbc_repo` commit `c527da39a`.
- Confirmed the testing lineage remains on `opendbc_repo` commit `2b55f0563`.
- Branch cleanup and remote ref removal verified separately after push.

### 2026-03-13

- Branches updated: `master`.
- Submodule commit(s): `c527da39a` - `subaru: smooth low-speed angle steering below 10mph`
- Why changed: promote low-speed angle smoothing (0-10 mph) into stable Subaru lateral path to reduce twitchy left-right corrections.
- Validation done: `python -m py_compile opendbc_repo/opendbc/car/subaru/carcontroller.py`.
- Known risks: requires in-car validation to confirm no regression in low-speed LKAS fault behavior.

### 2026-03-06

#### Superproject commits

- `f0b31f1` - `subaru: reduce angle LKAS faults in low-speed mads`
- `7405a43` - `subaru: fix angle LKAS cruise state handling`

#### Submodule (`opendbc_repo`) commits

- `72981fd` - `subaru: allow mads above 5mph with low-speed angle guard`
- `da845de` - `subaru: keep mads angle control above low-speed threshold`
- `3001604` - `subaru: gate angle LKAS requests to full-control drive state`
- `67e6381` - `subaru: use ES_Status cruise state for angle LKAS`

### 2026-03-05

#### Superproject commits

- `01e52bc` - `subaru: include 2025 outback fw fingerprint update`
- `f574e18` - `subaru: show 2025 outback in platform selector`

#### Submodule (`opendbc_repo`) commits

- `5e57cb7` - `subaru: add 2025 outback fw fingerprints`
- `5d3f9bc` - `subaru: expose outback 2025 in selector`
- `170e1de` - `subaru: port angle LKAS support and 2025 crosstrek platform`

## Functional Summary

- Added support path for modern Subaru angle-based steering.
- Added/updated 2025 Outback visibility and firmware fingerprint handling.
- Added low-speed/high-angle fault mitigation while preserving MADS behavior above 5 mph.
- No intentional changes were made to remove SunnyPilot features like MADS.

## Validation Notes

- Branches install correctly via installer URL.
- In-car behavior verified enough to detect and reproduce low-speed LKAS fault condition; mitigation patches added after log-driven debugging.
- Full long-duration, multi-cycle in-car validation is still required after each promoted change.

## Update Template (append for each new change set)

Use this section format for every future update:

```
### YYYY-MM-DD
- Branches updated: <master|MostlyClueless|both>
- Superproject commit(s): <hash> - <message>
- Submodule commit(s): <hash> - <message>
- Why changed: <short reason>
- Validation done: <road test / bench test / build check>
- Known risks: <if any>
```
