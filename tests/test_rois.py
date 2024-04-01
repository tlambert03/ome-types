from some_types import SOME, model


def test_roi_shapes() -> None:
    # this test is similar to what paquo does

    some = SOME()

    # --- create the roi
    roi = model.ROI(name="class_name")

    some_shape = model.Rectangle(height=1.0, width=1.0, x=1.0, y=1.0)
    roi.union.append(some_shape)
    assert some_shape in roi.union.rectangles

    # --- add the annotation to the some structure
    some.rois.append(roi)
    assert some.to_xml()
