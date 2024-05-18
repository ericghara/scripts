#!/bin/bash

# convert a (virtualbox) vmdk to (qemu) qcow2 disk image
# note need to use proprietary software to expand vmware ova file 
# (haven't found something oss that actually works for ova)
qemu-img convert -f vmdk -O qcow2 vm-iis-disk1.vmdk vm-iis-disk1.qcow2
