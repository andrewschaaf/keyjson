
import base64

from bitstring import BitString


def dumps64(x):
    return b64encode(dumps(x))

def loads64(data):
    return loads(b64decode(data))


###### keyjson-base64 ######

STANDARD_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
KEYJSON_ALPHABET = '()0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!'

def b64encode(data):
    return util_substitute(base64.b64encode(data), STANDARD_ALPHABET, KEYJSON_ALPHABET)

def b64decode(data):
    return base64.b64decode(util_substitute(data, KEYJSON_ALPHABET, STANDARD_ALPHABET))


###### keyjson ######

NULL = '\x31'
FALSE = '\x32'
TRUE = '\x33'
UNICODE = '\x34'
LIST = '\x35'
DICT = '\x36'

NEXT_ELEMENT = BitString('0b0')
MORE_BYTES = BitString('0b1')

def dumps(x):
    
    if x is None:   return NULL
    if x is False:  return FALSE
    if x is True:   return TRUE
    
    if isinstance(x, basestring):
        return UNICODE + unicode(x).encode('utf-8')
    
    if isinstance(x, int) or isinstance(x, long):
        return encode_int(x)
    
    if isinstance(x, list) or isinstance(x, tuple):
        return LIST + encode_datalist(dumps(elem) for elem in x)
    
    if isinstance(x, dict):
        keys = [(dumps(k), k) for k in x.keys()]
        arr = []
        for k_keyjson, k in sorted(keys):
            arr.append(k)
            arr.append(x[k])
        return DICT + encode_datalist(dumps(elem) for elem in arr)
    
    raise ValueError


def loads(data):
    
    assert isinstance(data, str) and len(data) > 0
    
    prefix = data[0]
    
    if prefix > '\x80':     return decode_int(data)
    if prefix == NULL:      return None
    if prefix == FALSE:     return False
    if prefix == TRUE:      return True
    if prefix == UNICODE:   return unicode(data[1:], 'utf-8')
    
    if prefix == LIST:
        return [loads(chunk) for chunk in decode_datalist(data[1:])]
    
    if prefix == DICT:
        arr = [loads(chunk) for chunk in decode_datalist(data[1:])]
        return dict(zip(util_evens(arr), util_odds(arr)))
    
    raise ValueError

###### keyjson-datalist ######

NEXT_ELEMENT = BitString('0b0')
MORE_BYTES = BitString('0b1')

def encode_datalist(x):
    return (NEXT_ELEMENT.join(
                MORE_BYTES.join(
                    BitString(bytes=byte)
                    for byte in data)
                for data in x)
            .tobytes()) # zero-pads if needed

def decode_datalist(x):
    
    # TODO find Book implementation
    
    def byte_isMore_tuples(x):
        numBits = len(x) * 8
        bs = BitString(bytes=x)
        pos = 0
        while numBits - pos >= 8:
            yield (
                        bs[pos:pos + 8].bytes,
                        bs[pos + 8] if (numBits - pos >= 9) else False)
            pos += 9
    
    datalist = []
    curDataBytes = []
    for byte, isMore in byte_isMore_tuples(x):
        curDataBytes.append(byte)
        if not isMore:
            datalist.append(''.join(curDataBytes))
            curDataBytes = []
    
    return datalist


###### keyjson-int ######

def encode_int(n):
    
    if n >= 0:
        if n < 128**1:          prefix, size, x = '\xC0', 1, n
        elif n < 128**2:        prefix, size, x = '\xC1', 2, n
        elif n < 128**3:        prefix, size, x = '\xC2', 3, n
        elif n < 128**4:        prefix, size, x = '\xC3', 4, n
        elif n < 128**5:        prefix, size, x = '\xC4', 5, n
        elif n < 128**6:        prefix, size, x = '\xC5', 6, n
        elif n < 128**7:        prefix, size, x = '\xC6', 7, n
        elif n < 128**8:        prefix, size, x = '\xC7', 8, n
        elif n < 128**9:        prefix, size, x = '\xC8', 9, n
        elif n < 128**10:       prefix, size, x = '\xC9', 10, n
    else:
        if n > -(128**1):       prefix, size, x = '\xBF', 1, n + (128**1 - 1)
        elif n > -(128**2):     prefix, size, x = '\xBE', 2, n + (128**2 - 1)
        elif n > -(128**3):     prefix, size, x = '\xBD', 3, n + (128**3 - 1)
        elif n > -(128**4):     prefix, size, x = '\xBC', 4, n + (128**4 - 1)
        elif n > -(128**5):     prefix, size, x = '\xBB', 5, n + (128**5 - 1)
        elif n > -(128**6):     prefix, size, x = '\xBA', 6, n + (128**6 - 1)
        elif n > -(128**7):     prefix, size, x = '\xB9', 7, n + (128**7 - 1)
        elif n > -(128**8):     prefix, size, x = '\xB8', 8, n + (128**8 - 1)
        elif n > -(128**9):     prefix, size, x = '\xB7', 9, n + (128**9 - 1)
        elif n > -(128**10):    prefix, size, x = '\xB6', 10, n + (128**10 - 1)
    
    chunks = []
    rshift = 7 * (size - 1)
    for i in range(size):
        chunks.append(chr(128 + ((x >> rshift) & 0x7F)))
        rshift -= 7
    
    return prefix + ''.join(chunks)


def decode_int(data):
    
    prefix = data[0]
    chunks = data[1:]
    size = len(chunks)
    
    x = 0
    lshift = 7 * (size - 1)
    for i in range(size):
        x |= ((ord(chunks[i]) - 128) << lshift)
        lshift -= 7
    
    if prefix >= '\xC0':
        return x
    else:
        return x - (128**size - 1)


###### util ######

def util_substitute(data, src, dest):
    return ''.join(dest[src.find(c)] for c in data)

def util_evens(stream):
    i = 0
    for x in stream:
        if i % 2 == 0:
            yield x
        i += 1

def util_odds(stream):
    i = 0
    for x in stream:
        if i % 2 == 1:
            yield x
        i += 1

