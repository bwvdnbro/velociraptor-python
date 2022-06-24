def register_new_catalogue_quantity(reader, path):
    unit = reader.get_unit(path)
    name = path.replace("/", " ")
    snake_case = path.lower().replace("/", "_")
    return unit, name, snake_case
