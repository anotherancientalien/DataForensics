#dataForensix.py
#this file is to complete the module assignment
#read basic information of a disk image file.
# NOTE: Assumption: the disk image file will always have a standard MBR
#author: paerhati.remutula, student ID 16099958
#date: 20170309  Last edit: 20170315

############################################################### Import libraries
import sys
import bitstring as bs
###################################################################### FUNCTIONS
#function 1: handles partition entry informations
def part_entry_info(partentry):
    entry_info_raw = partentry
    while int(str(partentry),16) != 0x00:
# NOTE: BitArray reading: offset,length = value * 8(bits per byte)
#"old"parttype = bs.BitArray(bytes=partentry,offset=32,length=8)#offset = 04 * 8
#reading from a bitarray: partentry[start:end:step], remember to * 8
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@ type of partition
        print(" Type of partition:",type_of_partition(partentry))
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@ starting sector
        print(" Starting sector:", starting_sector(partentry))
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@ size of partition
        print(" Size of partition (sectors):", size_of_partition(partentry))
        #end of part entry informations
        break
    else:
        print(" Partition doesn't exist.\n")

#function 2: print type_of_part
def type_of_partition(partentry):# top = type of partition
    parttype = partentry[32:40:] # position 04h , 4*8=32,size=1, (4+1)*8=40
    t = int(str(parttype),16)
    if t == 0x00:
        return("Unknown Or Empty")
    elif t == 0x01:
        return("12-bit FAT")
    elif t == 0x04:
        return("16-bit FAT")
    elif t == 0x05:
        return("Extended MS-DOS")
    elif t == 0x06:
        return("FAT 16")
    elif t == 0x07:
        return("NTFS")
    elif t == 0x0B:
        return("FAT 32(CHS)")
    elif t == 0x0C:
        return("FAT 32(LBA)")
    elif t == 0x0E:
        return("FAT 16(LBA)")
    else:
        return("Error recognizing type of partition")

# function 3: counts the number of partition
def number_of_partition(MBR):# takes in the partition entry raw
    # entry_info_raw = bs.BitArray(bytes=partentry)#partition entry
    # value = int(str(partentry))
    # partition entries learned from MBR
    entries = bs.BitArray(bytes=MBR,offset=446*8,length=16*8*4)
    n = 0 # count partitions
    entrieslist = []
    for entry in entries.cut(16*8):# 16 byte per entry, 8 bit per byte.
        entrieslist.append(entry)
    for entry in entrieslist:
        if int(str(entry),16) != 0:
            n += 1
    return(n) # counter problem fixed with this new approach.
    # for i in range(1,4):
    #     if int(str(entries[:16*8*i:16*8]),16) != ' ':
    #         n += 1
    # return(n)

# function 4: starting sector
def starting_sector(partentry):
    start_sec_raw = partentry[8*8:12*8:]
    start_sec = []
    # little-endian to big-endian convertion
    for byte in start_sec_raw.cut(8):
        start_sec.append(byte)
    start_sec = start_sec[::-1]
    start_sec = start_sec[0] + start_sec[1] + start_sec[2] + start_sec[3]
    return(int(str(start_sec),16))

# function 5: size of partition
def size_of_partition(partentry):
    #sector size = 512 bytes
    size_info_raw = partentry[12*8::]
    size_info = []
    # little-endian to big-endian convertion
    for byte in size_info_raw.cut(8):
        size_info.append(byte)
    size_info = size_info[::-1]
    size_info = size_info[0] + size_info[1] + size_info[2] + size_info[3]
    return(int(str(size_info),16))

# function 6: FAT volume information
# NOTE: this function is defined only for the FAT-16 partition.
def fat_volume(partentry):
    #taking partentry and determining starting sector:
    fat_start_sec_raw = partentry[8*8:12*8:]
    fat_start_sec = []
    #little-endian to big-endian convertion
    for byte in fat_start_sec_raw.cut(8):
        fat_start_sec.append(byte)
    fat_start_sec = fat_start_sec[::-1]
    fat_start_sec = fat_start_sec[0]+fat_start_sec[1]+fat_start_sec[2]+fat_start_sec[3]
    fat_start_sec = int(str(fat_start_sec),16)
    print("FAT starting sector in decimal: ",fat_start_sec)
    #################### Reading the raw data on FAT start sector:
    # Taking the data between MBR and sector 63 away.
    # the first 512 bytes are taken to MBR
    # take another 62 * 512 bytes away to reach the first sector of volume
    # so the "junk" will be (fat start sector)-1 # this 1 indicates the MBR in sector
    junk = f.read((fat_start_sec-1)*512) # current position: sector 63
    # print(len(junk))
    # now next 512 bytes will be the first sector of the volume
    # Read in the data of FAT volume first sector
    first_sector_of_volume = f.read(512) # current position: sector 64
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ number of sectors per cluster
    #print("first_sector_of_volume raw data:")
    #print(first_sector_of_volume)
    # number of sectors per cluster
    # offset 0Dh = 13, 13 * 8, length 1 byte, 1*8
    num_of_secpclus = bs.BitArray(bytes=first_sector_of_volume,offset=13*8,length=1*8)
    print("Number of sectors per cluster:",int(str(num_of_secpclus),16))
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ size of the FAT area
    # Size of the FAT area = size of FAT in sectors * number of FAT copies
    # size of FAT in sectors offset 16h,size 2, number of FAT copies offset 10h,size 1
    size_of_per_fat_raw = bs.BitArray(bytes=first_sector_of_volume,offset=22*8,length=2*8)
    # little-endian to big-endian convertion
    size_of_per_fat = []
    for byte in size_of_per_fat_raw.cut(8):
        size_of_per_fat.append(byte)
    size_of_per_fat = size_of_per_fat[::-1]
    size_of_per_fat = size_of_per_fat[0]+size_of_per_fat[1]
    # print(size_of_per_fat)
    # number of copies only one byte, no need to convert endian.
    num_of_fat_copies = bs.BitArray(bytes=first_sector_of_volume,offset=16*8,length=1*8)
    #print(num_of_fat_copies)
    size_of_fat_area = int(str(size_of_per_fat),16) * int(str(num_of_fat_copies),16)
    print("Size of the FAT area in sectors:",size_of_fat_area)
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ size of the root directory
    # size of root dir = max num of root dir entries * dir entry size in byte / sector size
    # max num of root dir entries offset 11h, size 2 bytes. 11h = 17d
    # dir size for a FAT is 32 bytes.
    # sector size = 512 bytes.
    dir_entry_size = 32
    sector_size = 512
    max_num_of_dir_raw = bs.BitArray(bytes=first_sector_of_volume,offset=17*8,length=2*8)
    # little-endian to big-endian convertion
    max_num_of_dir = []
    for byte in max_num_of_dir_raw.cut(8):
        max_num_of_dir.append(byte)
    max_num_of_dir = max_num_of_dir[::-1]
    max_num_of_dir = max_num_of_dir[0]+max_num_of_dir[1]
    max_num_of_dir = int(str(max_num_of_dir),16)
    # print(max_num_of_dir)
    # size of the root dir
    size_of_root_dir = int(max_num_of_dir * dir_entry_size / sector_size)
    print("Size of the Root Directory in sector:",size_of_root_dir)
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@ Sector address of cluster number 2.
    # sec_addr_of_clus_2 = first sector of data area + root dir size
    # first sec of data = first sec of volume + reserved area size + size of fat area
    # size of reserved area offset 0Eh = 14d
    # size of reserved area:
    size_of_reserved_raw = bs.BitArray(bytes=first_sector_of_volume,offset=14*8,length=2*8)
    #little-endian to big-endian convertion
    size_of_reserved = []
    for byte in size_of_reserved_raw.cut(8):
        size_of_reserved.append(byte)
    size_of_reserved = size_of_reserved[::-1]
    size_of_reserved = size_of_reserved[0]+size_of_reserved[1]
    size_of_reserved = int(str(size_of_reserved),16)
    print("size of reserved: ",size_of_reserved)
    # the first sec of volume and size of fat area are calculated before
    first_sec_of_data_area = int(str(fat_start_sec),16) + size_of_reserved + size_of_fat_area
    print("First sector of data area: ",first_sec_of_data_area)
    # sector addr of cluster 2
    sec_addr_of_clus_2 = first_sec_of_data_area + size_of_root_dir
    print("Sector address of Cluster No.2:")
    # 8 sectors per cluster
    print("    sector",sec_addr_of_clus_2,"to sector",sec_addr_of_clus_2 + 8,"\n")

    #@@@@@@@@@@@@@@@@@@@@@@@@@@ about the deleted file:
    print("--------------------------------")
    print("About the first deleted file in root directory: ")
    print("--------------------------------")
    # take away the unnecessary data from the disk image, i.e. keep reading till root dir
    # from above, f.read() reached the first sector of FAT volume.
    # take out the rest of reserved area:
    reserved_rest = f.read((size_of_reserved-1)*512) # current position: sector 65
    #take out the FAT area of this volume, 502 sectors, 512 bytes per sectors
    fat_area_raw_data = f.read(size_of_fat_area*512) # current position: sector 567
    # read in the root directory: size = 32 sector * 512 bytes.
    root_dir_raw_data = f.read(size_of_root_dir*512) # current position: sector 599
    # test if the correct data is read.
    # print(root_dir_raw_data)# tested
    #change the raw data to bit array:
    files_raw = bs.BitArray(bytes=root_dir_raw_data)
    # seperate the file entries within the root directory into an array
    file_entries = []
    for entry in files_raw.cut(32*8):# 32 bytes per entry.
        file_entries.append(entry)
    # print(file_entries) # tested, correct.
    # determining if an entry is an existing file
    existing_files = []
    for entry in file_entries:
        file_head = entry[:32:]
        if int(str(file_head),16) != 0:
            existing_files.append(entry)
    # determining if the file is deleted and take deleted file to a new array
    deleted_files = []
    for entry in existing_files:
        file_head = entry[:8:]
        # print(file_head) # tested, correct.
        if int(str(file_head),16) == 0xe5:
            deleted_files.append(entry)
    # print(deleted_files) # tested.
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ working on the first deleted file:
    while len(deleted_files) != 0:
        deleted_file = deleted_files[0]
        # file name offset : 0x00 to 0x0A
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ file name
        deleted_file_name = deleted_file[:11*8:]
        #deleted_file_name = codecs.decode("deleted_file_name","hex")
        del_filename_char = []
        for byte in deleted_file_name.cut(8):
            byte = chr(int(str(byte),16))
            del_filename_char.append(byte)
        print("The 1st Deleted file name: ",''.join(del_filename_char))
        # size of the file offset: 0x1C to 0x1F
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ file size
        deleted_file_size_raw = deleted_file[28*8:32*8:]
        #little-endian to big-endian convertion
        del_file_size = []
        for byte in deleted_file_size_raw.cut(8):
            del_file_size.append(byte)
        del_file_size = del_file_size[::-1]
        del_file_size = del_file_size[0]+del_file_size[1]+del_file_size[2]+del_file_size[3]
        # print(del_file_size) # tested.
        print("Deleted file size in bytes: ", int(str(del_file_size),16))
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ first cluster number of the file:
        # first cluster addr offset: 0x1A to 0x1B
        first_cluster_num_raw = deleted_file[26*8:28*8:]
        #little-endian to big-endian convertion
        first_cluster_num = []
        for byte in first_cluster_num_raw.cut(8):
            first_cluster_num.append(byte)
        first_cluster_num = first_cluster_num[::-1]
        first_cluster_num = first_cluster_num[0]+ first_cluster_num[1]
        first_cluster_num = int(str(first_cluster_num),16)
        print("Deleted file first cluster number: ", first_cluster_num)
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ "going" to the first cluster of the deleted file
        raw_data_on_cluster_2_17 = f.read((first_cluster_num-2)*8*512)
        # file current position: sector 735
        first_cluster_of_delfile_raw = f.read(8*512) # current position: sector 743
        # change bytes to bitarray.
        first_cluster_of_delfile = bs.BitArray(bytes=first_cluster_of_delfile_raw)
        # print(first_cluster_of_delfile_raw) # tested.
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@ first 16 characters of the file
        first_cluster_of_del_file = []
        for byte in first_cluster_of_delfile.cut(8):
            byte = chr(int(str(byte),16))
            first_cluster_of_del_file.append(byte)
        first_16_character = first_cluster_of_del_file[0:16]
        # NOTE: the line below prints first 16 raw characters
        #print("First 16 characters before formatting: ", first_16_character)
        print("First 16 characters of the deleted file: ", end='')
        print(''.join(first_16_character))
        break
    else:
        print("  Sorry, No deleted files found on this partition.")
        # NOTE: this prints "Section A" after skipping one line, this is because the
        # starting characters includes some formatting command. i.e. \n
        ################################################### End of FAT volume info.

# function 7: information about the NTFS volume.
def ntfs_info(ntfs_entry):
    start_sec_ntfs = starting_sector(ntfs_entry)
    # "going" to the ntfs volume:
    # NOTE: the beginning of the image file has already been read.
    # first 63 sectors + reserved of FAT + FAT area + root dir + (19-2) clusters
    # + first cluster of the del file
    # thus 1(MBR)+62(rest)+1(FAT_firstsec)+1(reservedrest)+502(fatarea)+32(rootdir)
    # +17*8(clus_not_mentioned)+1*8(first_clus_of_del_file) = 743 sectors.
    # so (starting sector 1606500) - (used 743 sectors of the file )
    # will take the file to the starting sector of the NTFS.
    print("Please wait for the tool to read info on NTFS...")
    junk_ntfs = f.read((start_sec_ntfs-743) * 512) # current position: sector 1606500
    # NOTE: method above will take a little more time to process, couldn't find
    # a better way to read the file.
    # the line above should take the file to offset 3106c800h
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ first sector of NTFS
    first_sector_of_ntfs = f.read(512) # current position: sector 1606501
    # testing if reading info correctly.
    # print(first_sector_of_ntfs) # tested.
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ bytes per sector:
    # bytes per sector offset 0Bh, size 2 byte.
    ntfs_byte_per_sec = bs.BitArray(bytes=first_sector_of_ntfs,offset=11*8,length=2*8)
    # print(ntfs_byte_per_sec) #tested.
    #little-endian to big-endian convertion
    ntfsbyte_per_sector = []
    for byte in ntfs_byte_per_sec.cut(8):
        ntfsbyte_per_sector.append(byte)
    ntfsbyte_per_sector = ntfsbyte_per_sector[::-1]
    ntfsbyte_per_sector = ntfsbyte_per_sector[0]+ntfsbyte_per_sector[1]
    print("NTFS Bytes per sector: ", int(str(ntfsbyte_per_sector),16))
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ sectors per cluster:
    # sectors per cluster offset 0x0D, size 1 byte.
    ntfs_sec_per_clus = bs.BitArray(bytes=first_sector_of_ntfs,offset=13*8,length=1*8)
    # one byte, no need to convert endian.
    ntfs_sectorPcluster = int(str(ntfs_sec_per_clus),16)
    print("NTFS sectors per cluster: ", ntfs_sectorPcluster)
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ sector address for the $MFT file
    # $MFT cluster address offset 0x30, remember to multiply by 8 sectors.
    MFT_cluster_addr = bs.BitArray(bytes=first_sector_of_ntfs,offset=48*8,length=8*8)
    # print(MFT_cluster_addr) # tested.
    # little-endian to big-endian convertion
    Mca = [] # Mca as in "MFT cluster address"
    for byte in MFT_cluster_addr.cut(8):
        Mca.append(byte)
    Mca = Mca[::-1]
    # print(Mca) # tested.
    Mca= Mca[0]+Mca[1]+Mca[2]+Mca[3]+Mca[4]+Mca[5]+Mca[6]+Mca[7]
    Mca = int(str(Mca),16)
    # Mca is the cluster address, sector address = first sector of NTFS + Mca
    Msa = Mca * 8 + start_sec_ntfs
    print("Sector address of the $MFT file: ", Msa)
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ type and length of first two attribute
    # NOTE: attribute type offset 0-3d, length 4byte
    # NOTE: attribute length offset 4-7d, length 4byte.
    # reading the $MFT data:
    # 4 cluster * 8 sec_per_clus =32, already read the first 1 sector, so 31*512.
    to_mft_junk = f.read((Mca*8-1)*512) # current position: sector 1606532
    mft_file_raw = f.read(2*512) # current position: sector 1606533
    # print(mft_file_raw) # tested.
    # offset to the first attribute: 20-21d, 0x14-0x15
    ######## first attribute location offset
    first_attrib = bs.BitArray(bytes=mft_file_raw,offset=20*8,length=2*8)
    #little-endian to big-endian convertion
    first_attribute = []
    for byte in first_attrib.cut(8):
        first_attribute.append(byte)
    first_attribute = first_attribute[::-1]
    first_attribute = first_attribute[0]+first_attribute[1]
    first_attribute = int(str(first_attribute),16)
    # print(first_attribute) # value 56d, 0x38, tested.
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ first attribute_type_identifier
    attribute_type_id = bs.BitArray(bytes=mft_file_raw,offset=first_attribute*8,length=4*8)
    # little-endian to big-endian convertion
    attrTpID = []
    for byte in attribute_type_id.cut(8):
        attrTpID.append(byte)
    attrTpID = attrTpID[::-1]
    attrTpID = attrTpID[0]+attrTpID[1]+attrTpID[2]+attrTpID[3]
    attrTpID = int(str(attrTpID),16)
    print("\nType of the first attribute: ", attribute_type_text(attrTpID))
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ first attribute length
    attrib_length_raw = bs.BitArray(bytes=mft_file_raw,offset=(first_attribute+4)*8,length=4*8)
    # little-endian to big-endian convertion
    attrlen = []
    for byte in attrib_length_raw.cut(8):
        attrlen.append(byte)
    attrlen = attrlen[::-1]
    attrlen = attrlen[0]+attrlen[1]+attrlen[2]+attrlen[3]
    attrlen = int(str(attrlen),16)
    print("Length of the first attribute: ", attrlen)
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ second attribute type.
    # offset of second attribute = offset of 1st + 1st length.
    offset_of_2nd = first_attribute + attrlen
    attr2_raw = bs.BitArray(bytes=mft_file_raw,offset=offset_of_2nd*8,length=4*8)
    # little-endian to big-endian convertion
    attr2_type = []
    for byte in attr2_raw.cut(8):
        attr2_type.append(byte)
    attr2_type = attr2_type[::-1]
    attr2_type = attr2_type[0]+ attr2_type[1]+attr2_type[2]+attr2_type[3]
    # print(attr2_type) # tested.
    attr2_type = int(str(attr2_type),16)
    print("\nType of the second attribute: ", attribute_type_text(attr2_type))
    #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ second attribute length
    attr2_len_raw = bs.BitArray(bytes=mft_file_raw,offset=(offset_of_2nd+4)*8,length=4*8)
    # little-endian to big-endian convertion
    attr2_len = []
    for byte in attr2_len_raw.cut(8):
        attr2_len.append(byte)
    attr2_len = attr2_len[::-1]
    attr2_len = attr2_len[0]+attr2_len[1]+attr2_len[2]+attr2_len[3]
    attr2_len = int(str(attr2_len),16)
    print("Length of the second attribute: ", attr2_len)

# function 7.1: NTFS attribute type identifier
def attribute_type_text(attrTpID):
    if attrTpID == 16:
        return("$STANDARD_INFORMATION")
    elif attrTpID == 32:
        return("$ATTRIBUTE_LIST")
    elif attrTpID == 48:
        return("$FILE_NAME")
    elif attrTpID == 64:
        return("$OBJECT_ID")
    elif attrTpID == 80:
        return("$SECURITY_DESCRIPTOR")
    elif attrTpID == 96:
        return("$VOLUME_NAME")
    elif attrTpID == 122:
        return("$VOLUME_INFORMATION")
    elif attrTpID == 128:
        return("$DATA")
    elif attrTpID == 144:
        return("$INDEX_ROOT")
    elif attrTpID == 160:
        return("$INDEX_ALLOCATION")
    elif attrTpID == 176:
        return("$BITMAP")
    elif attrTpID == 192:
        return("$REPARSE_POINT")
    elif attrTpID == 256:
        return("$LOGGED_UTILITY_STREAM")
    else:
        return("Error determining Attribute type")

############################### let the tool take in a disk image file parameter
# Usage: python3 dataForensix.py Sample_1.dd
dd = sys.argv[1]
# NOTE: this parameter function is not completed, needs further work

########################################################### Try to read .dd file
with open(dd, 'rb') as f:
    # Read file test
    # IDEA: add another check point later: if file name == *.dd, then go on
    # if f.read(1) != "":
    # NOTE: cannot use f.read() for testing as it reads(consume) 1 byte of the
    #file, causing the whole file reading messed up.
    #     print("\nDisk image <%s> successfully loaded!\n" % dd)
    # else:
    #     print("\nError loading <%s>...\n" % dd)

    ##########################################Reading file into string variables
    #MBR:
    MBR = f.read(512) # current position: sector 1
    firstpartentry = bs.BitArray(bytes=MBR,offset=446*8,length=16*8)
    secondpartentry = bs.BitArray(bytes=MBR,offset=(446+1*16)*8,length=16*8)
    thirdpartentry = bs.BitArray(bytes=MBR,offset=(446+2*16)*8,length=16*8)
    fourthpartentry = bs.BitArray(bytes=MBR,offset=(446+3*16)*8,length=16*8)
    bootrecordsignature = bs.BitArray(bytes=MBR,offset=(446+4*16)*8,length=2*8)
    ############################################################# say hi to user
    print("Hello, you are using disk image %s" % dd)
    print("********************************")
    print("Basic information")
    print("********************************")
    ####################################################### Number of partitions
    print("Number of partitions:", number_of_partition(MBR))
    ################################################ first partition information
    print("\nFirst partition:"),part_entry_info(firstpartentry)
    ############################################### Second partition information
    print("\nSecond partition:"),part_entry_info(secondpartentry)
    ################################################ Third partition information
    print("\nThird partition:"),part_entry_info(thirdpartentry)
    ############################################### Fourth partition information
    print("\nFourth partition:"),part_entry_info(fourthpartentry)
    ################################################# Detail of FAT 16 partition
    # defining a FAT entry and an NTFS entry:
    all_entries = [firstpartentry,secondpartentry,thirdpartentry,fourthpartentry]
    fat_entry = ''
    ntfs_entry = ''
    for entry in all_entries:
        if int(str(entry[32:40:]),16) == 0x06:
            fat_entry = entry
        elif int(str(entry[32:40:]),16) == 0x07:
            ntfs_entry = entry
    print("********************************")
    print("Specific Information of the FAT partition:")
    print("********************************")
    while fat_entry != '':
        fat_volume(fat_entry)
        break
    else:
        print("  Sorry, No useful information found")
    ################################################## Detail of the NTFS volume
    print("********************************")
    print("Specific Information of the NTFS partition: ")
    print("********************************")
    while ntfs_entry != '':
        ntfs_info(ntfs_entry)
        break
    else:
        print("  Sorry, No useful information found.")

f.close()
# NOTE: change ascii value to hex value method: hex = format(ord("ascii"),"x")
# NOTE: default format of print() function is to go to next line after print
# print("some text", end=' ') will put this line and next print on the same line.
