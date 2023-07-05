import os
from pathlib import Path

import pytest
from omero.gateway import BlitzGateway
from omero_cli_transfer import populate_omero, populate_xml

from ome_types import OME, model


@pytest.fixture(scope="session")
def data_dir(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("data")


HOST = "omero-app.hms.harvard.edu"
PORT = 4064


@pytest.fixture(scope="session")
def conn() -> BlitzGateway:
    user = os.environ["OMERO_USER"]
    passwd = os.environ["OMERO_PASSWORD"]
    conn = BlitzGateway(user, passwd, host=HOST, port=PORT)
    conn.connect()
    try:
        assert conn.isConnected()
        yield conn
    finally:
        conn.close()


@pytest.mark.parametrize(
    "datatype, id",
    [
        # ("Dataset", 21157),
        # ("Project", 9834),
        ("Project", 5414),
        ("Project", 3654),
        # ("Project", 451),
    ],
)
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_populate_xml(
    conn: BlitzGateway, data_dir: Path, datatype: str, id: int
) -> None:
    dest = data_dir / "new.ome.xml"
    ome, _ = populate_xml(
        datatype=datatype,
        id=id,
        filepath=str(dest),
        conn=conn,
        hostname=HOST,
        barchive=False,  # write the file
        metadata=[],
    )
    assert isinstance(ome, OME)
    assert dest.exists()
    assert isinstance(OME.from_xml(str(dest)), OME)


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_populate_omero(conn: BlitzGateway, data_dir: Path) -> None:
    plate = model.Plate()
    annotations = [model.CommentAnnotation(value="test comment")]
    ome = OME(plates=[plate], structured_annotations=annotations)
    populate_omero(
        ome, img_map={}, conn=conn, hash="somehash", folder=data_dir, metadata=[]
    )
