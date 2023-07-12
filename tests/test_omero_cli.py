from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from ome_types import OME

if TYPE_CHECKING:
    from pathlib import Path

    from omero.gateway import BlitzGateway
    from pytest import MonkeyPatch, TempPathFactory


# this test can be run with only `pip install omero-cli-transfer --no-deps`
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_populate_omero(monkeypatch: MonkeyPatch, full_ome_object: OME) -> None:
    monkeypatch.setitem(sys.modules, "omero.gateway", MagicMock())
    monkeypatch.setitem(sys.modules, "omero.rtypes", MagicMock())
    monkeypatch.setitem(sys.modules, "omero.model", MagicMock())
    monkeypatch.setitem(sys.modules, "omero.sys", MagicMock())
    monkeypatch.setitem(sys.modules, "ezomero", MagicMock())

    gen_omero = pytest.importorskip("generate_omero_objects")

    conn = MagicMock()
    getId = conn.getUpdateService.return_value.saveAndReturnObject.return_value.getId
    getId.return_value.val = 2

    gen_omero.populate_omero(
        full_ome_object,
        img_map={"Image:0": (1, 2, 3)},
        conn=conn,
        hash="somehash",
        folder="",
        metadata=["md5", "img_id", "plate_id", "timestamp"],
    )
    assert conn.method_calls


@pytest.fixture(scope="session")
def data_dir(tmp_path_factory: TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("data")


@pytest.fixture(scope="session")
def conn() -> BlitzGateway:
    pytest.importorskip("omero.gateway")

    from omero.gateway import BlitzGateway

    user = os.environ["OMERO_USER"]
    passwd = os.environ["OMERO_PASSWORD"]
    host = os.environ["OMERO_HOST"]
    conn = BlitzGateway(user, passwd, host=host, port=4064)
    conn.connect()
    try:
        assert conn.isConnected()
        yield conn
    finally:
        conn.close()


# To run this test, you must have omero-py installed and have the following
# environment variables set:
# OMERO_USER
# OMERO_PASSWORD
# OMERO_HOST
@pytest.mark.skipif("OMERO_USER" not in os.environ, reason="OMERO_USER not set")
@pytest.mark.parametrize(
    "datatype, id",
    [
        ("Dataset", 21157),
        ("Project", 5414),
        ("Image", 1110952),
    ],
)
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_populate_xml(
    data_dir: Path,
    datatype: str,
    id: int,
    conn: BlitzGateway,
) -> None:
    from omero_cli_transfer import populate_xml

    dest = data_dir / "new.ome.xml"
    ome, _ = populate_xml(
        datatype=datatype,
        id=id,
        filepath=str(dest),
        conn=conn,
        hostname="host",
        barchive=False,  # write the file
        metadata=[],
    )
    assert isinstance(ome, OME)
    assert dest.exists()
    ome2 = OME.from_xml(dest)
    assert ome2 == ome
