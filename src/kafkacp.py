import random
import math
from datetime import datetime
from openopt import *
from numpy import sin, cos

# Seeding the random number generator
random.seed(datetime.now())

VCPU = "vcpu"
MEM = "mem"
NETWORK_IN = "networkin"
NETWORK_OUT = "networkout"
EBS_BANDWIDTH = "ebs-bandwidth"
TOPIC = "topic"
DATARATE = "datarate"
MESSAGE_SIZE = "messsage-size"
CONSUMERS = "consumers"
REPLAYS = "replays"
REPLAY_RATE = "replay-rate"
PARTITIONS = "partitions"
REPLICATION_FACTOR = "replication-factor"
MAX_LAG = "max-lag"
REPLICA_ID = "replica-id"
PARTITION_ID = "partition-id"

ec2_instance_types = {
    "m4.large": {
        VCPU: 2,
        MEM: 8 * 1024,
        EBS_BANDWIDTH: 450 / 8,
        NETWORK_IN: 125,
        NETWORK_OUT: 125
    },
    "m4.xlarge": {
        VCPU: 4,
        MEM: 16 * 1024,
        EBS_BANDWIDTH: 750 / 8,
        NETWORK_IN: 125,
        NETWORK_OUT: 125
    },
    "m4.2xlarge": {
        VCPU: 8,
        MEM: 32 * 1024,
        EBS_BANDWIDTH: 1000 / 8,
        NETWORK_IN: 125,
        NETWORK_OUT: 125
    },
    "m4.4xlarge": {
        VCPU: 16,
        MEM: 64 * 1024,
        EBS_BANDWIDTH: 2000 / 8,
        NETWORK_IN: 125,
        NETWORK_OUT: 125
    },
    "m4.10xlarge": {
        VCPU: 40,
        MEM: 160 * 1024,
        EBS_BANDWIDTH: 4000 / 8,
        NETWORK_IN: 1250,
        NETWORK_OUT: 1250
    },
    "m4.16xlarge": {
        VCPU: 64,
        MEM: 256 * 1024,
        EBS_BANDWIDTH: 10000 / 8,
        NETWORK_IN: 2500,
        NETWORK_OUT: 2500
    }
}

N = 3
MILLION = 1000000
HUNDRED_THOUSAND = 100000
INDEX_SIZE = 10

topics = []

for i in range(N):
    data_rate = MILLION + HUNDRED_THOUSAND * random.randint(5, 30)
    max_lag = random.randint(5, 20) * data_rate
    topics.append({
        TOPIC: "t-%d" % i,
        DATARATE: data_rate,
        MESSAGE_SIZE: 100 + 10 * random.randint(2, 10),
        CONSUMERS: random.randint(1, 6),
        REPLAYS: random.randint(1, 4),
        REPLAY_RATE: random.randint(1, 3) * data_rate,
        PARTITIONS: random.randint(8, 15),
        REPLICATION_FACTOR: 3,
        MAX_LAG: max_lag
    })

items = []

for t in topics:
    topic = t[TOPIC]
    partitions = t[PARTITIONS]
    message_size = t[MESSAGE_SIZE]
    per_part_datarate = ((t[DATARATE] * message_size) / MILLION) / partitions
    consumers = t[CONSUMERS]
    replays = t[REPLAYS]
    replication_factor = t[REPLICATION_FACTOR]
    replay_rate = ((t[REPLAY_RATE] * message_size) / MILLION) / partitions
    max_lag = t[MAX_LAG] / partitions
    for p in range(partitions):
        items.append({
            TOPIC: topic,
            NETWORK_IN: per_part_datarate,
            NETWORK_OUT: (consumers + replication_factor - 1) * per_part_datarate + replays * replay_rate,
            EBS_BANDWIDTH: per_part_datarate + replays * replay_rate,
            MEM: INDEX_SIZE + ((max_lag * message_size) / MILLION),
            PARTITION_ID: p,
            REPLICA_ID: 0
        })
        # Replicas also need to support replays and consumers incase leaders goes down
        for j in range(replication_factor - 1):
            items.append({
                TOPIC: topic,
                NETWORK_IN: per_part_datarate,
                NETWORK_OUT: (consumers + replication_factor - 1) * per_part_datarate + replays * replay_rate,
                EBS_BANDWIDTH: per_part_datarate + replays * replay_rate,
                MEM: INDEX_SIZE + ((max_lag * message_size) / MILLION),
                PARTITION_ID: p,
                REPLICA_ID: j + 1
            })

max_network_out = max(items, key=lambda item: item[NETWORK_OUT])[NETWORK_OUT]
max_ebs = max(items, key=lambda item: item[EBS_BANDWIDTH])[EBS_BANDWIDTH]
max_mem = max(items, key=lambda item: item[MEM])[MEM]

print 'items', len(items)
print 'max network out', max_network_out
print 'max ebs bandwidth', max_ebs
print 'max mem', max_mem

least_suitable_instance_type = None
for key, value in ec2_instance_types.iteritems():
    if value[NETWORK_OUT] > max_network_out * 2 and value[EBS_BANDWIDTH] > max_ebs * 2:
        least_suitable_instance_type = key
        break

print 'least suitable instance type', least_suitable_instance_type
sum_network_out = sum(p[NETWORK_OUT] for p in items)
instance_count_lower_bound = math.ceil(
    sum_network_out / ec2_instance_types[least_suitable_instance_type][NETWORK_OUT]) + 1

bins = {
    NETWORK_OUT: ec2_instance_types[least_suitable_instance_type][NETWORK_OUT],
    NETWORK_IN: ec2_instance_types[least_suitable_instance_type][NETWORK_IN],
    EBS_BANDWIDTH: ec2_instance_types[least_suitable_instance_type][EBS_BANDWIDTH],
    MEM: ec2_instance_types[least_suitable_instance_type][MEM]
}


p = BPP(items, bins, goal='min')
# p = BPP(items, bins, goal = 'min')
r = p.solve('glpk', iprint=0)

for i, s in enumerate(r.xf):
    print "bin " + str(i) + " has " + str(len(s)) + " items"
