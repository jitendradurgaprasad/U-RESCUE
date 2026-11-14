import numpy as np
from u_rescue.terrain import process

def test_two_hgt_tiles_mosaic_and_clip(tmp_path):
    source=tmp_path/"raw"; source.mkdir()
    tile=np.full((1201,1201),500,dtype=">i2")
    (source/"n17e077.hgt").write_bytes(tile.tobytes())
    (source/"n17e078.hgt").write_bytes(tile.tobytes())
    before=(source/"n17e077.hgt").stat().st_size
    result=process(source,tmp_path/"out",stride=12,study_bbox=[77.5,17.5,78.5,18.0])
    grid=np.load(tmp_path/"out"/"terrain_risk_grid.npz")
    assert result["source_tiles"]==["n17e077","n17e078"]
    assert result["bounds"]==[77.5,17.5,78.5,18.0]
    assert grid["elevation"].shape==(51,101)
    assert np.allclose(grid["risk"],grid["risk"][0,0])
    assert (source/"n17e077.hgt").stat().st_size==before
