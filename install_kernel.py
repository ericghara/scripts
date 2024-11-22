#!/bin/python3
 
from pathlib import Path
import re
import shutil
 
WHERE_KERNEL_IS = '/boot'
WHERE_KERNEL_SHOULD_GO = '/boot/EFI/Gentoo'
KERNEL_SOURCES = '/usr/src'
OLD_KERNELS_SHOULD_GO = '/boot/EFI/Gentoo/old'
# newest n kernels should stay where kernel should go, older ones should go to old kernels
num_new = 3 

if __name__ == '__main__':                                                                                                                                             
    src_dir = Path(WHERE_KERNEL_IS)
    dest_dir = Path(WHERE_KERNEL_SHOULD_GO)
    kernel_src_dir = Path(KERNEL_SOURCES)
    old_kernel_dir = Path(OLD_KERNELS_SHOULD_GO)

    version_grabber = re.compile(r'(\d+\.\d+\.\d+-gentoo(-r\d)?)(\.\w{3})?$')
 
    def move_new_kernels():
        print("# Moving new kernels")
        seen = set()
        for f in src_dir.glob('kernel-[0-9]*.[0-9]*.[0-9]*-gentoo*'):
            res = version_grabber.search(f.name)
            if not res:
                print(f"! Skipping {f.name}")
                continue
            print(f"* Moving {f.name} to {src_dir}")
            f.rename(dest_dir.joinpath(f.name))
            version = res.group(1)
            if version not in seen:
                seen.add(version)
                expected_source = kernel_src_dir.joinpath('linux-' + version, '.config')
                if not expected_source.is_file():
                    print(f"Cannot move config for kernel {version}, not found!")
                else:
                    shutil.copy2(expected_source, dest_dir.joinpath(f"config-{version}"))
                    print(f"* Moving config for kernel: {version}")

    def intern_old_kernels():
        
        class Manifest:

            def __init__(self):
                self.files = list()
                self.oldest_ctime = float('inf')

            def __repr__(self):
                return f'Manifest(files={self.files}, oldest_ctime={self.oldest_ctime})'

        print("# Interning old kernels")
        kernel_files = dict()

        for f in dest_dir.glob('*'):
            res = version_grabber.search(f.name)
            if not res:
                print(f"* Skipping {f.name}")
                continue
            
            manifest = kernel_files.setdefault(res.group(1), Manifest())
            manifest.files.append(f)
            manifest.oldest_ctime = min(manifest.oldest_ctime, f.stat().st_ctime)
        
        to_intern = sorted(kernel_files.values(), key=lambda m: m.oldest_ctime)[:-1 * num_new]
        for m in to_intern:
            for f in m.files:
                print(f"* moving {f.name} to {old_kernel_dir}")
                f.rename(old_kernel_dir.joinpath(f.name))
                
    move_new_kernels()
    intern_old_kernels()

