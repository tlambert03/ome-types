from ome_types import OME, model


def test_roi_shapes() -> None:
    # this test is similar to what paquo does

    ome = OME()

    # --- create the roi
    roi = model.ROI(name="class_name")

    ome_shape = model.Rectangle(height=1.0, width=1.0, x=1.0, y=1.0)
    roi.union.append(ome_shape)
    assert ome_shape in roi.union.rectangles

    # --- add the annotation to the ome structure
    ome.rois.append(roi)
    assert ome.to_xml()
