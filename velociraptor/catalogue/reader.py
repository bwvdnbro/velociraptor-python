import h5py
import os
import unyt


class H5ls:
    def __init__(self):
        self.paths = []

    def __call__(self, name, h5obj):
        if hasattr(h5obj, "dtype"):
            # strip leading '/'
            self.paths.append(h5obj.name[1:])

    def get_paths(self):
        return self.paths


class VelociraptorCatalogueReader:
    def __init__(self, filename):
        with h5py.File(filename, "r") as handle:
            if ("Parameters" in handle) and (
                "vr_basename" in handle["Parameters"].attrs
            ):
                self.type = "new"
                snap_nr = handle["Parameters"].attrs["snapshot_nr"]
                vr_basename = handle["Parameters"].attrs["vr_basename"] % {
                    "snap_nr": snap_nr
                }
                self.vr_filename = f"{vr_basename}.properties"
                if not os.path.exists(self.vr_filename):
                    self.vr_filename = f"{self.vr_filename}.0"
                    if not os.path.exists(self.vr_filename):
                        raise FileNotFoundError(
                            f"Could not find VR catalogue {self.vr_filename}!"
                        )
            else:
                self.type = "old"
                self.vr_filename = filename

            self.filename = filename

    def get_name(self):
        return self.filename

    def get_vr_name(self):
        return self.vr_filename

    def get_datasets(self):
        h5ls = H5ls()
        with h5py.File(self.filename, "r") as handle:
            handle.visititems(h5ls)
        return h5ls.get_paths()

    def get_unit_and_shape(self, field):
        with h5py.File(self.filename, "r") as handle:
            unitdict = dict(handle[field].attrs)
            shape = handle[field].shape
        factor = (
            unitdict["Conversion factor to CGS (including cosmological corrections)"][0]
            * unyt.A ** unitdict["U_I exponent"][0]
            * unyt.cm ** unitdict["U_L exponent"][0]
            * unyt.g ** unitdict["U_M exponent"][0]
            * unyt.K ** unitdict["U_T exponent"][0]
            * unyt.s ** unitdict["U_t exponent"][0]
        )
        return factor, shape

    def read_field(self, field, mask, unit, component=None):
        with h5py.File(self.filename, "r") as handle:
            if component is None:
                return unyt.unyt_array(handle[field][mask], unit)
            else:
                return unyt.unyt_array(handle[field][mask][:, component], unit)