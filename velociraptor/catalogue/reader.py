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
                self.vr_filename = (
                    f'{handle["Parameters"].attrs["vr_basename"]}.properties'
                )
                if not os.path.exists(self.vr_filename):
                    self.vr_filename = f"{self.vr_filename}.0"
                    if not os.path.exists(self.vr_filename):
                        raise RuntimeError("Could not find VR catalogue!")
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

    def read_field(self, field, mask, unit):
        with h5py.File(self.filename, "r") as handle:
            if self.type == "old":
                return unyt.unyt_array(handle[field][mask], unit)
            else:
                data = handle[field][mask]
                unitdict = dict(handle[field].attrs)
                factor = (
                    unitdict[
                        "Conversion factor to CGS (including cosmological corrections)"
                    ][0]
                    * unyt.A ** unitdict["U_I exponent"][0]
                    * unyt.cm ** unitdict["U_L exponent"][0]
                    * unyt.g ** unitdict["U_M exponent"][0]
                    * unyt.K ** unitdict["U_T exponent"][0]
                    * unyt.s ** unitdict["U_t exponent"][0]
                )
                factor.convert_to_units(unit)
                data *= factor
                data.convert_to_units(unit)
                return data
