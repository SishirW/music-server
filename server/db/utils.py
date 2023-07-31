from bson.json_util import dumps


def get_json_data_from_list(data):
    list_cur = list(data)
    json_data = dumps(list_cur)

    return json_data
