"# DataForensics" 
This is a simple disk investigating tool, written in Python3.6. An assignment of module DataForensics. 

This tool assumes that a disk image file <example.dd> with a standard MBR will be used.

Prints out information about the disk image as follows:
* Number of partitions on the disk
* For each partition: Partition type, Starting sector, Partition size in sectors
* For a FAT16 partition: Number of sectors per cluster, size of the FAT area, size of the Root directory, sector address of cluster no.2, and some detailed information about the first deleted file in this partition.
* For an NTFS partition: Number of bytes per sector, number of sectors per cluster, sector address of the $MFT record, Type and length of the first two attributes in $MFT

This tool is written to complete the module assignment.

A disk image file can be created using FTK imager, which also can be used to explore raw data on a hard disk.
