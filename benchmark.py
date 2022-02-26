from timeit import timeit 
from tabulate import tabulate

import sys 

message = '''d = {
    'int_single': 1539,
    'float_single': 33.333,
    'string_single': "MEGA_GAMER_2222",
    'int_list': list(range(1000)),
    'float_list': list(i / 3 for i in range(1000)),
    'string_list': list(str(i) for i in range(1000)),
    'dict': dict((str(i), i) for i in iter(range(1000))),  
    'string_large': """
		Pentos is a large port city, more populous than Astapor on Slaver Bay, 
		and may be one of the most populous of the Free Cities. 
		It lies on the bay of Pentos off the narrow sea, with the Flatlands 
		plains and Velvet Hills to the east.
		The city has many square brick towers, controlled by the spice traders. 
		Most of the roofing is done in tiles. There is a large red temple in 
		Pentos, along with the manse of Illyrio Mopatis and the Sunrise Gate 
		allows the traveler to exit the city to the east, 
		in the direction of the Rhoyne.
		""" * 100
}'''

setup_pickle    = '%s; import pickle ; src = pickle.dumps(d, 2)' % message
setup_json      = '%s; import json; src = json.dumps(d)' % message
setup_proto     = '%s; from benchmark_pb2 import Message; from google.protobuf.json_format import ParseDict; msg = Message(); msg = ParseDict(d, msg); src = msg.SerializeToString()' % message
setup_xml       = '%s; import plistlib; src = plistlib.dumps(d)' % message
setup_yaml      = '%s; import yaml; src = yaml.dump(d)' % message
setup_msgpack   = '%s; import msgpack; src = msgpack.packb(d)' % message

init_avro       = '%s; import io, avro.io; s = avro.schema.parse(open("benchmark.avsc").read())' % message
write_avro      = 'bw = io.BytesIO(); enc = avro.io.BinaryEncoder(bw); dw = avro.io.DatumWriter(s); dw.write(d, enc); src = bw.getvalue()'
read_avro       = 'br = io.BytesIO(src); dc = avro.io.BinaryDecoder(br); dr = avro.io.DatumReader(s); dr.read(dc)'
setup_avro      = f'{init_avro}; {write_avro}; {read_avro}'

tests = [
    # (title, setup, enc_test, dec_test)
    ('pickle (native serialization)', setup_pickle, 'pickle.dumps(d, 2)', 'pickle.loads(src)'),
    ('json',  setup_json, 'json.dumps(d)', 'json.loads(src)'),
    ('protobuf', setup_proto, 'msg.SerializeToString()', 'msg.ParseFromString(src)'),
    ('xml', setup_xml, 'plistlib.dumps(d)', 'plistlib.loads(src)'),
    ('yaml', setup_yaml, 'yaml.dump(d)', 'yaml.full_load(src)'),
    ('msgpack', setup_msgpack, 'msgpack.packb(d)', 'msgpack.unpackb(src)'),
    ('avro', setup_avro, write_avro, read_avro)
]
loops = 1000
enc_table = []
dec_table = []
 
print ("Running tests (%d loops each)" % loops)
 
for title, mod, enc, dec in tests:
    print(title)
 
    print("  [Encode]", enc) 
    result = timeit(enc, mod, number=loops)
    exec(mod)
    enc_table.append([title, result, sys.getsizeof(src)])
 
    print("  [Decode]", dec) 
    result = timeit(dec, mod, number=loops)
    dec_table.append([title, result])
 
enc_table.sort(key=lambda x: x[1])
enc_table.insert(0, ['Package', 'Seconds', 'Size'])
 
dec_table.sort(key=lambda x: x[1])
dec_table.insert(0, ['Package', 'Seconds'])
 
print("\nEncoding Test (%d loops)" % loops)
print(tabulate(enc_table, headers="firstrow"))
 
print("\nDecoding Test (%d loops)" % loops)
print(tabulate(dec_table, headers="firstrow"))