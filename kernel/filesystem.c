

#include "filesystem.h"
#include "stdlib.h"
#include "fs_archive.h"
#include "kdefs.h"

extern superblock_t *ramdisk_superblock;
extern filesystem_archive_t fs_archive[];


/*
 * Initializes the in-memory filesystem.
 * This involves setting up the superblock,
 * inode table, unpacking the filesystem
 * archive, and mounting the device filesystem.
 */
void init_filesystem()
{
    superblock_t superblock;
    superblock.num_inodes = NUM_INODES;
    superblock.inode_table_start = INODE_TABLE_BLOCK_NUMBER;
    memset(&superblock.free_inode_bitmap, 0xff, NUM_INODES/8);
    memset(&superblock.free_block_bitmap, 0xff, RAMDISK_SIZE/(BLOCK_SIZE*8));
    set_block_in_use(&superblock, SUPERBLOCK_NUMBER);
    
    int num_blocks_inode_table = (superblock.num_inodes*sizeof(inode_t))/BLOCK_SIZE;

    // in case inode table only uses part of the last block
    if((superblock.num_inodes*sizeof(inode_t))%BLOCK_SIZE) num_blocks_inode_table++;

    for(int i = 0; i < num_blocks_inode_table; i++)
    {
        set_block_in_use(&superblock, superblock.inode_table_start + i);
    }


    memcopy(ramdisk_superblock, &superblock, sizeof(superblock_t));
    

    unpack_filesystem_archive(fs_archive);

    // TODO: add dev filesystem
}



static int is_inode_free(superblock_t *superblock, inode_number_t inode_index)
{
    int is_free;
    int byte_index = inode_index/8;
    int bit_index = inode_index%8;
    is_free = ( superblock->free_inode_bitmap[byte_index] >> bit_index ) & 0x1;
    return is_free;
}

static void set_inode_free(superblock_t *superblock, inode_number_t inode_index)
{
    int byte_index = inode_index/8;
    int bit_index = inode_index%8;
    unsigned char mask = 0x1 << bit_index;
    superblock->free_inode_bitmap[byte_index] |= mask;
}

static void set_inode_in_use(superblock_t *superblock, inode_number_t inode_index)
{
    int byte_index = inode_index/8;
    int bit_index = inode_index%8;
    unsigned char mask = ~(0x1 << bit_index);
    superblock->free_inode_bitmap[byte_index] &= mask;
}

static inode_number_t get_next_free_inode_number(superblock_t *superblock)
{
    inode_number_t index;
    for(index = 0; index < superblock->num_inodes; index++)
    {
        int byte_index = index/8;
        int bit_index = index%8;
        if(is_inode_free(superblock, index))
        {
            break;
        }
    }

    if(index >= superblock->num_inodes)
    {
        index = -1;
    }

    return index;
}



static int is_block_free(superblock_t *superblock, block_number_t block_number)
{
    short byte_index = block_number/8;
    short bit_index = block_number%8;

    int is_free = (superblock->free_block_bitmap[byte_index] >> bit_index) & 0x1;

    return is_free;
}


static void set_block_free(superblock_t *superblock, block_number_t block_number)
{
    short byte_index = block_number/8;
    short bit_index = block_number%8;
    unsigned char mask = 0x1 << bit_index;

    superblock->free_block_bitmap[byte_index] |= mask;
}


static void set_block_in_use(superblock_t *superblock, block_number_t block_number)
{
    short byte_index = block_number/8;
    short bit_index = block_number%8;
    unsigned char mask = ~(0x1 << bit_index);

    superblock->free_block_bitmap[byte_index] &= mask;
}


static block_number_t get_next_free_block_number(superblock_t *superblock)
{
    block_number_t block_number;

    for(block_number = 0; block_number < RAMDISK_SIZE/BLOCK_SIZE; block_number++)
    {
        if(is_block_free(superblock, block_number))
        {
            break;
        }
    }

    if(block_number >= RAMDISK_SIZE/BLOCK_SIZE)
    {
        block_number = 0;
    }

    return block_number;
}




int is_open_file_free(open_file_table_t *open_file_table, int number)
{
    int byte_index = number/8;
    unsigned char bit_index = number%8;
    int is_free = (open_file_table->free_spot_bitmap[byte_index] >> bit_index) & 0x1;

    return is_free;
}

static void set_open_file_free(open_file_table_t *open_file_table, int number)
{
    int byte_index = number/8;
    unsigned char bit_index = number%8;
    unsigned char mask = 0x1 << bit_index;

    open_file_table->free_spot_bitmap[byte_index] |= mask;
}


static void set_open_file_in_use(open_file_table_t *open_file_table, int number)
{
    int byte_index = number/8;
    unsigned char bit_index = number%8;
    unsigned char mask = ~(0x1 << bit_index);

    open_file_table->free_spot_bitmap[byte_index] &= mask;
}

static int find_first_free_open_file(open_file_table_t *open_file_table)
{
    int index;

    for(index = 0; index < MAX_OPEN_FILES; index++)
    {
        if(is_open_file_free(open_file_table, index))
        {
            break;
        }
    }

    if(index >= MAX_OPEN_FILES)
    {
        index = OPEN_FILE_TABLE_FULL;
    }

    return index;
}



static void add_directory_entry(superblock_t *superblock, inode_t *directory_inode, dir_entry_t *entry)
{
    write_file(superblock, directory_inode, entry, directory_inode->file_size, sizeof(dir_entry_t));
}




/*
 * Uses the list of directory entries passed
 * to is to initialize it as the root directory
 * of the filesystem.
 */
void create_root(dir_entry_t *root_dir, int num_entries)
{
    /*
     * The base address of the ramdisk is where the superblock
     * is stored, so cast this pointer to use.
     */
    superblock_t *superblock = ramdisk_superblock;

    inode_t *inode_table = GET_POINTER_FROM_BLOCK_NUMBER(superblock->inode_table_start);
    short inode_index = get_next_free_inode_number(superblock);
    set_inode_in_use(superblock, inode_index);
    
    superblock->root_inode_index = inode_index;
    inode_t root_entry = inode_table[inode_index];
    root_entry.file_type = FILE_TYPE_DIRECTORY;
    root_entry.file_size = 0;

    memset(&root_entry.block_numbers, 0, INODE_BLOCK_LIST_SIZE*sizeof(block_number_t));
    root_entry.block_numbers[0] =  get_next_free_block_number(superblock);
    set_block_in_use(&superblock, root_entry.block_numbers[0]);

    for(int i = 0; i < num_entries; i++)
    {
        add_directory_entry(&root_entry, &root_dir[i]);
    }

    root_entry.file_size = sizeof(dir_entry_t)*num_entries;
}



static int get_next_filename(char **path, char *filename)
{
    if(**path == "\0")
        return 0;
    
    while(**path != "\0" && **path != "/")
    {
        *filename = **path;
        *path++;
        filename++;
    }

    *filename = "\0";
    
    if(**path == "/") *path++; 

    return 1;
}



static inode_t *get_root_dir(superblock_t *superblock)
{
    inode_t *inode_table = GET_POINTER_FROM_BLOCK_NUMBER(superblock->inode_table_start);
    return &inode_table[superblock->root_inode_index];
}



/*
 * Given an offset into a file, returns the block number at that
 * offset. Accounts for single and double indirect blocks.
 */
static block_number_t get_block_number_from_file_offset(inode_t *inode, unsigned short offset)
{
    block_number_t block_number;

    // if offset is strictly greater than the file size, give error
    if(offset > inode->file_size)
    {
        block_number = SUPERBLOCK_NUMBER;
    }

    /*
     * In the case where the offset is equal to to the file size, and the
     * end of the file takes of the entire last block, the next 
     */
    if(offset == inode->file_size && (GET_BLOCK_OFFSET_FROM_FILE_OFFSET(offset) == 0))
    {
        block_number = SUPERBLOCK_NUMBER;
    }

    if(offset < FIRST_SINGLE_INDIRECT_OFFSET())
    {
        short block_index = offset/BLOCK_SIZE;
        block_number = inode->block_numbers[block_index];
    }
    else if(offset < FIRST_DOUBLE_INDIRECT_OFFSET())
    {
        // get the block number of the indirect block
        block_number_t indirect_block_number = inode->block_numbers[FIRST_SINGLE_INDIRECT_BLOCK_INDEX];

        // offset now stores the offset into the indirect block
        offset -= FIRST_SINGLE_INDIRECT_OFFSET();

        // get the index into the indirect block of the block with the data
        short block_index = offset/BLOCK_SIZE;

        // get pointer to actual indirect block
        block_number_t *block = GET_POINTER_FROM_BLOCK_NUMBER(indirect_block_number);

        // block number of the block that stores data
        block_number = block[block_index];
    }
    else if(offset < MAX_OFFSET())
    {
        block_number_t first_layer_block_number = inode->block_numbers[FIRST_DOUBLE_INDIRECT_BLOCK_INDEX];
        offset -= FIRST_DOUBLE_INDIRECT_OFFSET();
        block_number_t *first_layer_blocks = GET_POINTER_FROM_BLOCK_NUMBER(first_layer_block_number);


        /*
         * The index into the first layer of indirect blocks gives the block
         * number of the second layer block. Each second layer block contains
         * the block numbers of the actual data blocks. Data will be filled
         * starting with index 0 of the first layer and index 0 of the second
         * layer. Thus, the file will start using index 1 of the first layer
         * after using up all indices of the second layer for index 0 of the
         * first layer. Thus, the amount of data stored into the file in index
         * 0 of the first layer is BLOCK_SIZE*num_block_numbers, where
         * num_block_numbers is the maximum number of block numbers stored on
         * the second layer block. This is equal to BLOCK_SIZE/sizeof(block_number_t).
         * The index into the first layer block is offset/total data stored
         * by each first layer block, which is BLOCK_SIZE*BLOCK_SIZE/sizeof(block_number_t).
         */
        short first_layer_block_index = offset/(BLOCK_SIZE*BLOCK_SIZE/sizeof(block_number_t));

        block_number_t second_layer_block_number = first_layer_blocks[first_layer_block_index];
        block_number_t *second_layer_blocks = GET_POINTER_FROM_BLOCK_NUMBER(second_layer_block_number);

        /*
         * Offset into second layer block. Given by subtracting the total amount of data
         * stored in the first_block_index blocks from offset. The total amount of data
         * stored in the first_block_index blocks is first_block_index multiplied
         * by the amount of data stored by each first layer block, which is BLOCK_SIZE
         * squared over the size of each block number. This may look like it should come
         * out to 0 since this is the inverse of the first_block_index calculation above,
         * but since first_block_index was calculated using integer division, there may
         * be some remainder left over.
         */
        offset -= first_layer_block_index*(BLOCK_SIZE*BLOCK_SIZE/sizeof(block_number_t));
        
        short second_layer_block_index = offset/BLOCK_SIZE;
        block_number = second_layer_blocks[second_layer_block_index];
    }
    else
    {
        block_number = SUPERBLOCK_NUMBER;
    }

    return block_number;
}



int is_valid_file_type(type)
{
    int is_valid = (type == FILE_TYPE_REGULAR)      ||
                   (type == FILE_TYPE_DIRECTORY)    ||
                   (type == FILE_TYPE_CHAR)         ||
                   (type == FILE_TYPE_BLOCK)        ||
                   (type == FILE_TYPE_NET)          ||
                   (type == FILE_TYPE_TIMER)        ||
                   (type == FILE_TYPE_GPIO)         ||
                   (type == FILE_TYPE_ADC)          ||
                   (type == FILE_TYPE_PWM);

    return is_valid;
}



unsigned char make_major_and_minor(major, minor)
{
    // TODO
}



static int get_dir_entry(inode_t *inode, dir_entry_t *entry, int entry_number)
{
    unsigned short offset = entry_number * sizeof(dir_entry_t);

    if(read_file(inode, entry, offset, sizeof(dir_entry_t)) != sizeof(dir_entry_t))
    {
        return DIR_ENTRY_NOT_FOUND_ERROR;
    }

    return 0;
}




static block_number_t append_new_file_block(superblock_t *superblock, inode_t *inode)
{
    block_number_t block_number;

    // direct blocks
    if(inode->file_size < FIRST_SINGLE_INDIRECT_OFFSET())
    {
        int index;

        // find first free direct block
        for(index = 0; index < FIRST_SINGLE_INDIRECT_BLOCK_INDEX; index++)
        {
            if(inode->block_numbers[index] == SUPERBLOCK_NUMBER)
            {
                break;
            }
        }

        // if no free direct block, return error
        if(index >= FIRST_SINGLE_INDIRECT_BLOCK_INDEX) return SUPERBLOCK_NUMBER;

        // get new block from free pool and add to inode block list
        block_number = get_next_free_block_number(superblock);
        set_block_in_use(superblock, block_number);
        inode->block_numbers[index] = block_number;
    }

    // single indirect block
    else if(inode->file_size < FIRST_DOUBLE_INDIRECT_OFFSET())
    {
        // check if single indirect block has been added and add single indirect block
        if(inode->block_numbers[FIRST_SINGLE_INDIRECT_BLOCK_INDEX] == SUPERBLOCK_NUMBER)
        {
            inode->block_numbers[FIRST_SINGLE_INDIRECT_BLOCK_INDEX] = get_next_free_block_number(superblock);
            memset(GET_POINTER_FROM_BLOCK_NUMBER(inode->block_numbers[FIRST_SINGLE_INDIRECT_BLOCK_INDEX]), 0, BLOCK_SIZE);
        }

        block_number_t *single_indirect_blocks = GET_POINTER_FROM_BLOCK_NUMBER(inode->block_numbers[FIRST_SINGLE_INDIRECT_BLOCK_INDEX]);
        int index;

        for(index = 0; index < BLOCK_SIZE/sizeof(block_number_t); index++)
        {
            if(single_indirect_blocks[index] == SUPERBLOCK_NUMBER)
            {
                break;
            }
        }

        single_indirect_blocks[index] = get_next_free_block_number(superblock);
        set_block_in_use(superblock, single_indirect_blocks[index]);
        block_number = single_indirect_blocks[index];
    }

    // double indirect block
    else if(inode->file_size < MAX_OFFSET())
    {
        short file_size = inode->file_size;
        short single_indirect_index;
        short double_indirect_index;
        block_number_t double_indirect_block_number;
        block_number_t *single_indirect_blocks;
        block_number_t *double_indirect_blocks;

        // if first layer indirect block not allocated, then allocate
        if(inode->block_numbers[FIRST_DOUBLE_INDIRECT_BLOCK_INDEX] == SUPERBLOCK_NUMBER)
        {
            inode->block_numbers[FIRST_DOUBLE_INDIRECT_BLOCK_INDEX] = get_next_free_block_number(superblock);
            memset(GET_POINTER_FROM_BLOCK_NUMBER(inode->block_numbers[FIRST_DOUBLE_INDIRECT_BLOCK_INDEX]), 0, BLOCK_SIZE);
        }

        // offset into double indirect blocks
        file_size -= FIRST_DOUBLE_INDIRECT_OFFSET();

        /*
         * To get first layer indirect block index, must take into account
         * the total size of data that can be stored by each second layer indirect
         * block. Each second layer indirect block can store BLOCK_SIZE/sizeof(block_number_t)
         * block numbers, and each block referenced by the block numbers can store BLOCK_SIZE
         * bytes of data, so the total amount of data stored by the second layer indirect
         * block referenced by each block number in the first layer indirect block is
         * BLOCK_SIZE*BLOCK_SIZE/(block_number_t). Thus to get the index, take the
         * offset or file size and divide (integer division) it by the amount of data
         * stored by each second layer indirect block.
         */
        single_indirect_index = file_size/(BLOCK_SIZE*BLOCK_SIZE/sizeof(block_number_t));
        single_indirect_blocks = GET_POINTER_FROM_BLOCK_NUMBER(inode->block_numbers[FIRST_DOUBLE_INDIRECT_BLOCK_INDEX]);
        double_indirect_block_number = single_indirect_blocks[single_indirect_index];
        double_indirect_blocks = GET_POINTER_FROM_BLOCK_NUMBER(double_indirect_block_number);


        // find first free index in 2nd layer indirect blocks 
        for(double_indirect_index = 0; double_indirect_index < BLOCK_SIZE/sizeof(block_number_t); double_indirect_index++)
        {
            if(double_indirect_blocks[double_indirect_index] == SUPERBLOCK_NUMBER)
            {
                break;
            }
        }

        // get block, set in use, and add to double indirect list
        block_number = get_next_free_block_number(superblock);
        set_block_in_use(block_number);
        double_indirect_blocks[double_indirect_index] = block_number;
    }

    // file too large
    else
    {
        block_number = SUPERBLOCK_NUMBER;
    }

    return block_number;
}



/*
 * Gets a pointer to the given inode from the inode number.
 */
static inode_t *get_inode(superblock_t *superblock, inode_number_t inode_number)
{
    inode_t *inode_table = GET_POINTER_FROM_BLOCK_NUMBER(superblock->inode_table_start);
    return &inode_table[inode_number];
}



static inode_number_t get_inode_number_from_inode(superblock_t *superblock, inode_t *inode)
{
    inode_t *inode_table = GET_POINTER_FROM_BLOCK_NUMBER(superblock->inode_table_start);

    return (inode - inode_table)/sizeof(inode_t);
}



inode_number_t get_containing_directory(superblock_t *superblock, char *path)
{
    inode_t *current_dir = NULL_POINTER;
    char current_file[MAX_FILENAME_LENGTH];
    dir_entry_t current_entry;

    if(strlen(path) >= MAX_PATH_LENGTH)
    {
        return -1;
    }

    // all paths must start with /
    if(path[0] != "/")
    {
        return -1;
    }
    
    // eat first slash
    path++;
    current_dir = get_root_dir(superblock);

    
    // while loop performs recursive lookup
    while(get_next_filename(&path, current_file))
    {
        // file cannot be found
        if(current_dir->file_type != FILE_TYPE_DIRECTORY)
        {
            return -1;
        }

        int num_entries = current_dir->file_size/sizeof(dir_entry_t);

        // search for file name in directory
        int i;
        for(i = 0; i < num_entries; i++)
        {
            get_dir_entry(current_dir, &current_entry, i);
            if(string_compare(current_file, current_entry.filename, MAX_FILENAME_LENGTH))
            {
                break;
            }
        }

        // file not found in directory
        if(i >= num_entries)
        {
            return -1;
        }

        // found file. Get inode from inode number and repeat
        current_dir = get_inode(superblock, current_entry.inode_number);
    }

    return get_inode_number_from_inode(superblock, current_dir);
}


inode_number_t recursive_lookup(superblock_t *superblock, char *path)
{
    inode_t *current_dir = NULL_POINTER;
    char current_file[MAX_FILENAME_LENGTH];
    dir_entry_t current_entry;

    if(strlen(path) >= MAX_PATH_LENGTH)
    {
        return -1;
    }

    // all paths must start with /
    if(path[0] != "/")
    {
        return -1;
    }
    
    // eat first slash
    path++;
    current_dir = get_root_dir(superblock);

    
    // while loop performs recursive lookup
    while(get_next_filename(&path, current_file))
    {
        // file cannot be found
        if(current_dir->file_type != FILE_TYPE_DIRECTORY)
        {
            return -1;
        }

        int num_entries = current_dir->file_size/sizeof(dir_entry_t);

        // search for file name in directory
        int i;
        for(i = 0; i < num_entries; i++)
        {
            get_dir_entry(current_dir, &current_entry, i);
            if(string_compare(current_file, current_entry.filename, MAX_FILENAME_LENGTH))
            {
                break;
            }
        }

        // file not found in directory
        if(i >= num_entries)
        {
            return -1;
        }

        // found file. Get inode from inode number and repeat
        current_dir = get_inode(superblock, current_entry.inode_number);
    }

    return current_entry.inode_number;
}


int is_device_file(inode_t *inode)
{
    int is_dev = (inode->file_type == FILE_TYPE_CHAR)  ||
                 (inode->file_type == FILE_TYPE_BLOCK) ||
                 (inode->file_type == FILE_TYPE_NET)   ||
                 (inode->file_type == FILE_TYPE_TIMER) ||
                 (inode->file_type == FILE_TYPE_GPIO)  ||
                 (inode->file_type == FILE_TYPE_ADC)   ||
                 (inode->file_type == FILE_TYPE_PWM);
    
    return is_dev;
}



int open_file(superblock_t *superblock, open_file_table_t *open_file_table, char *path)
{
    inode_number_t inode_number;
    int open_file_index;
    inode_t *inode;

    // perform recursive path lookup to get the inode number
    inode_number = recursive_lookup(superblock, path);
    inode = get_inode(superblock, inode_number);

    // add to open file table
    open_file_index = find_first_free_open_file(open_file_table);
    set_open_file_in_use(open_file_table, open_file_index);
    open_file_table->open_files[open_file_index].cursor = 0;
    open_file_table->open_files[open_file_index].inode_number = inode_number;

    // if file is device file, need to run device open procedure
    if((inode->file_type == FILE_TYPE_CHAR) ||
        (inode->file_type == FILE_TYPE_BLOCK) ||
        (inode->file_type == FILE_TYPE_NET))
        {
            // TODO: device-specific open procedure.
        }

    return open_file_index;
}


int close_file(superblock_t *superblock, open_file_table_t *open_file_table, int file_descriptor)
{
    memset(&open_file_table->open_files[file_descriptor], 0, sizeof(open_file_table_entry_t));
    set_open_file_free(open_file_table, file_descriptor);

    return 0;
}



/*
 * Reads data from the file pointed to by inode into buffer. Offset is
 * the starting point to read from and size is the number of bytes.
 * Returns the number of bytes read from the file. If this is less than
 * size, that indicates an error.
 */
int read_file(inode_t *inode, void *buffer, unsigned short offset, unsigned short size)
{
    block_number_t block_to_read;
    unsigned char block_offset;
    short bytes_to_read;
    short bytes_read = 0;

    // TODO: char, block, and net devices


    // continue reading from file blocks until no data left
    while(size > 0)
    {
        if(block_to_read = get_block_number_from_file_offset(inode, offset) == SUPERBLOCK_NUMBER)
        {
            break;
        }

        block_offset = GET_BLOCK_OFFSET_FROM_FILE_OFFSET(offset);
        bytes_to_read = (size > (BLOCK_SIZE - block_offset) ) ? (BLOCK_SIZE - block_offset) : size;

        // copy data from block to buffer
        memcopy(buffer, GET_POINTER_FROM_BLOCK_NUMBER_AND_OFFSET(block_to_read, block_offset), bytes_to_read);
        
        // update read and write pointers and bytes left to read
        buffer += bytes_to_read;
        offset += bytes_to_read;

        bytes_read += bytes_to_read;
        size -= bytes_to_read;
    }

    return bytes_read;
}



int write_file(superblock_t *superblock, inode_t *inode, void *buffer, unsigned short offset, unsigned short size)
{
    block_number_t block_number;
    unsigned short block_offset;
    unsigned short bytes_to_write;
    unsigned short bytes_written = 0;
    void *current_block;
    

    // TODO: char, block, net devices

    if(offset > inode->file_size)
    {
        return bytes_written;
    }


    while(size > 0)
    {
        block_number = get_block_number_from_file_offset(inode, offset);

        if((block_number == SUPERBLOCK_NUMBER) && (offset == inode->file_size) && (offset%BLOCK_SIZE == 0))
        {
            block_number = append_new_file_block(superblock, inode);
        }

        block_offset = GET_BLOCK_OFFSET_FROM_FILE_OFFSET(offset);
        current_block = GET_POINTER_FROM_BLOCK_NUMBER_AND_OFFSET(block_number, block_offset);

        /* 
         * Number of bytes to write to the given block is minimum of 
         * total amount left to write and amount left on a given block.
         */
        bytes_to_write = (size < (BLOCK_SIZE - block_offset)) ? size : (BLOCK_SIZE - block_offset);

        memcopy(current_block, buffer, bytes_to_write);

        // increment read and write pointers
        buffer += bytes_to_write;
        offset += bytes_to_write;

        // decrement amount left to write
        size -= bytes_to_write;

        // increment total amount written
        bytes_written += bytes_to_write;
    }

    return bytes_written;
}


int create_file(superblock_t *superblock, int type, char *file_path, short major, short minor)
{
    inode_number_t dir_inode_number = get_containing_directory(superblock, file_path);
    inode_t *directory_inode = get_inode(superblock, dir_inode_number);

    dir_entry_t entry;
    strncpy(entry.filename, file_path, MAX_FILENAME_LENGTH);
    entry.inode_number = get_next_free_inode_number(superblock);
    set_inode_in_use(superblock, entry.inode_number);
    

    // initialize inode struct
    inode_t *inode = get_inode(superblock, entry.inode_number);
    memset(inode->block_numbers, 0, INODE_BLOCK_LIST_SIZE*sizeof(block_number_t));
    
    if(is_valid_file_type(type))
        inode->file_type = type;
    
    inode->file_size = 0;

    if(is_device_file)
        inode->major_and_minor = make_major_and_minor(major, minor);


    if(dir_inode_number < 0)
    {
        return -1;
    }

    add_directory_entry(superblock, directory_inode, &entry);

    return 0;
}



int delete_file(superblock_t *superblock, open_file_table_t *open_file_table, char *file_path)
{
    int open_file_index;
    inode_number_t inode_number = recursive_lookup(superblock, file_path);
    set_inode_free(superblock, inode_number);

    for(int open_file_index = 0; open_file_index < MAX_OPEN_FILES; open_file_index++)
    {
        if (open_file_table->open_files[open_file_index].inode_number == inode_number)
        {
            break;
        }
    }

    if(open_file_index < MAX_OPEN_FILES)
    {
        set_open_file_free(open_file_table, open_file_index);
    }


    return 0;
}