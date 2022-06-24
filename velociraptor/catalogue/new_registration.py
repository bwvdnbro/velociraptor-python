def get_group_and_name(path):
    path_groups = path.split("/")
    if path_groups[0] == "SO":
        SOname_groups = path_groups[1].split("_")
        ref = SOname_groups[-1]
        if ref in ["mean", "crit"]:
            ref = f"rho{ref}"
        rest = ""
        if len(SOname_groups) > 1:
            rest = f"{rest.join(SOname_groups[:-1])}_"
        SOname = f"{rest}{ref}"
        name_group = path_groups[2]
        return (
            "spherical_overdensities",
            f"{name_group} ({SOname})",
            f"{name_group}_{SOname}",
        )
    elif path_groups[0] == "ExclusiveSphere":
        aperture_name = path_groups[1]
        name_group = path_groups[2]
        return (
            "apertures",
            f"{name_group} ({aperture_name})",
            f"{name_group}_{aperture_name}",
        )
    elif path_groups[0] == "ProjectedAperture":
        aperture_name = path_groups[1]
        aperture_projection = path_groups[2][-1]
        aperture_number = {"x": 0, "y": 1, "z": 2}[aperture_projection]
        name_group = path_groups[3]
        return (
            "projected_apertures",
            f"{name_group} ({aperture_name} {aperture_projection})",
            f"{name_group}_{aperture_name}_{aperture_number}",
        )
    else:
        return "fail_all", path, path.lower().replace("/", "_")


def register_new_catalogue_quantity(reader, path):
    unit, shape = reader.get_unit_and_shape(path)
    if len(shape) > 1:
        components = shape[1]
    else:
        components = 1
    name = path.replace("/", " ")
    registration_function, full_name, snake_case = get_group_and_name(path)
    return unit, name, snake_case, registration_function, components
