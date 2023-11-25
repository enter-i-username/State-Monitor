import numpy as np
import msgpack


def pack_dict(msg_dict):
    new_dict = dict()

    for _key, _value in msg_dict.items():
        if isinstance(_value, np.ndarray):
            new_dict[_key] = pack_array(_value)
        else:
            new_dict[_key] = _value

    new_dict['HeLlO'] = 'wOrLd'
    binary_code = msgpack.packb(new_dict)
    return binary_code


def unpack_dict(binary_code):
    try:
        new_dict = msgpack.unpackb(binary_code, raw=False)
    except:
        return None

    if 'HeLlO' in new_dict.keys() and new_dict['HeLlO'] == 'wOrLd':
        new_dict.pop('HeLlO')

        for _key, _value in new_dict.items():
            if isinstance(_value, dict):
                try:
                    nparray = unpack_array(_value)
                    new_dict[_key] = nparray
                except:  # KeyError or something else
                    pass

            else:
                pass

        return new_dict
    else:
        return None


def pack_array(data):
    shape = tuple(data.shape)
    data_seq = data.ravel()

    tensor_dict = dict()
    tensor_dict['shape'] = shape
    tensor_dict['dtype'] = str(data_seq.dtype)
    tensor_dict['data'] = data_seq.tobytes()

    return tensor_dict


def unpack_array(tensor_dict):
    shape = tensor_dict['shape']
    dtype = tensor_dict['dtype']
    data_seq = tensor_dict['data']
    data = np.frombuffer(data_seq, dtype=dtype).reshape(shape)

    return data



