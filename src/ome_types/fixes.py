from __future__ import annotations

from typing import TYPE_CHECKING

from ome_types._conversion import OME_2016_06_URI

if TYPE_CHECKING:
    from ome_types._conversion import AnyElementTree


NSMAP = {"": OME_2016_06_URI, "ome": OME_2016_06_URI}


def fix_micro_manager_instrument(tree: AnyElementTree) -> AnyElementTree:
    """Fix MicroManager Instrument and Detector IDs and References."""
    for i_idx, instrument in enumerate(tree.findall("Instrument", NSMAP)):
        old_id = instrument.get("ID")
        if old_id.startswith("Microscope"):
            new_id = f"Instrument:{i_idx}"
            instrument.set("ID", new_id)
            for ref in tree.findall(f".//InstrumentRef[@ID='{old_id}']", NSMAP):
                ref.set("ID", new_id)

        for d_idx, detector in enumerate(instrument.findall(".//Detector", NSMAP)):
            old_id = detector.get("ID")
            if not old_id.startswith("Detector:"):
                new_id = f"Detector:{old_id if old_id.isdigit() else d_idx}"
                detector.set("ID", new_id)
                for ref in tree.findall(f".//DetectorSettings[@ID='{old_id}']", NSMAP):
                    ref.set("ID", new_id)

    return tree


ALL_FIXES = [fix_micro_manager_instrument]
