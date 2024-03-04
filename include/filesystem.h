


#ifndef FILESYSTEM_H
#define FILESYSTEM_H



#define FILE_PATH_TOO_LONG_ERROR    -1
#define FILE_NOT_FOUND_ERROR        -2
#define DIR_ENTRY_NOT_FOUND_ERROR   -3


// in future make this configurable via kernel.cfg
#define MAX_FILENAME_LENGTH 16
#define MAX_PATH_LENGTH 128

#define MAX_DIRECTORY_ENTRIES 64

//  size of block list in inode
#define INODE_BLOCK_LIST_SIZE 8

#define MAX_OPEN_FILES 64
#define OPEN_FILE_TABLE_FULL -1

#define SUPERBLOCK_NUMBER 0


#define FIRST_SINGLE_INDIRECT_BLOCK_INDEX 6
#define FIRST_DOUBLE_INDIRECT_BLOCK_INDEX 7

#define FIRST_SINGLE_INDIRECT_OFFSET()    (FIRST_SINGLE_INDIRECT_BLOCK_INDEX*BLOCK_SIZE)

#define FIRST_DOUBLE_INDIRECT_OFFSET()                      \
    (FIRST_SINGLE_INDIRECT_BLOCK_INDEX*BLOCK_SIZE +         \
    (BLOCK_SIZE/sizeof(block_number_t))*BLOCK_SIZE)

#define MAX_OFFSET()                                        \
    (FIRST_SINGLE_INDIRECT_BLOCK_INDEX*BLOCK_SIZE +         \
    (BLOCK_SIZE/sizeof(block_number_t))*BLOCK_SIZE +        \
    (BLOCK_SIZE/sizeof(block_number_t))*(BLOCK_SIZE/sizeof(block_number_t))*BLOCK_SIZE)


#define MINOR_NUMBER_MASK 0x7
#define MINOR_NUMBER_BITS 3


// will make fully configurable later
#define BLOCK_SIZE 64
#define RAMDISK_SIZE 16384

#define NUM_INODES 64
#define INODE_TABLE_BLOCK_NUMBER 1      // starts at second block

/*
 * Macros defining different file types.
 */
#define FILE_TYPE_REGULAR           0
#define FILE_TYPE_DIRECTORY         1
#define FILE_TYPE_CHAR              2
#define FILE_TYPE_BLOCK             3
#define FILE_TYPE_NET               4
#define FILE_TYPE_TIMER             5
#define FILE_TYPE_GPIO              6
#define FILE_TYPE_ADC               7
#define FILE_TYPE_PWM               8
#define FILE_TYPE_NONE              255


/*
 * Configure the filesystem to use
 * 8 bit integers to represent block
 * and inode numbers as long as the
 * number of blocks can be represented
 * using 8 bits.
 * 
 * Otherwise use 16 bit block numbers
 * and if 16 bits is not enough, use
 * 32 bits. This helps to save space
 * in memory.
 */
#if RAMDISK_SIZE/BLOCK_SIZE > 65536
#define USE_32_BIT_FS
#elif RAMDISK_SIZE/BLOCK_SIZE > 256
#define USE_16_BIT_FS
#endif

#if defined(USE_16_BIT_FS)
typedef unsigned short block_number_t;
#elif defined (USE_32_BIT_FS)
typedef unsigned int block_number_t;
#else
typedef unsigned char block_number_t;
#endif


#if (NUM_INODES < 128)          // max val of signed char
typedef char inode_number_t;
#elif (NUM_INODES < 32768)      // max val of signed short
typedef short inode_number_t;
#else
typedef int inode_number_t;
#endif





/*
 * Data structure definitions. Note that
 * directory and inode table are not defined,
 * but the entries in each are. This is
 * because each structure has a size defined
 * for it and is just a table of entries.
 */
typedef struct DIRENT
{
    char filename[MAX_FILENAME_LENGTH];
    inode_number_t inode_number;

} dir_entry_t;


typedef struct INODE
{
    short file_size;
    unsigned int file_type:8;

    /*
     * Only for device files. The upper
     * 5 bits of this field are the major
     * number, or the driver type. The least
     * significant 3 bits are the minor or
     * device number.
     */
    unsigned int major_and_minor:8;

    // permissions, timestamp, etc.

    block_number_t block_numbers[INODE_BLOCK_LIST_SIZE];

} inode_t;


#define GET_DRIVER_TYPE(_inode) ( (inode)->major_and_minor >> MINOR_NUMBER_BITS)
#define GET_DEVICE_NUMBER(_inode) ( (inode)->major_and_minor & MINOR_NUMBER_MASK)



 


typedef struct SUPERBLOCK
{
    /*
     * Block number of beginning of
     * inode table.
     */
    block_number_t inode_table_start;

    /*
     * Number of inodes in
     * the inode table.
     */
    unsigned short num_inodes;


    unsigned char free_inode_bitmap[NUM_INODES/8];
    unsigned char free_block_bitmap[RAMDISK_SIZE/(BLOCK_SIZE*8)];

    short root_inode_index;

} superblock_t;



typedef struct OPEN_FILE_ENTRY
{
    short cursor;     // current position in the file
    inode_number_t inode_number;

} open_file_table_entry_t;

typedef struct OPEN_FILE_TABLE
{
    open_file_table_entry_t open_files[MAX_OPEN_FILES];
    unsigned char free_spot_bitmap[MAX_OPEN_FILES/8];
} open_file_table_t;




#define GET_POINTER_FROM_BLOCK_NUMBER(_block_number) (ramdisk_superblock + _block_number*BLOCK_SIZE)
#define GET_POINTER_FROM_BLOCK_NUMBER_AND_OFFSET(_block_number, _offset) (ramdisk_superblock + _block_number*BLOCK_SIZE + _offset)
#define GET_BLOCK_NUMBER_FROM_POINTER(_pointer)             ((_pointer - ramdisk_superblock)/BLOCK_SIZE)
#define GET_BLOCK_OFFSET_FROM_POINTER(_pointer)             ((_pointer - ramdisk_superblock)%BLOCK_SIZE)
#define GET_BLOCK_OFFSET_FROM_FILE_OFFSET(_file_offset)     (_file_offset%BLOCK_SIZE)



/*
 * Initial filesystem image will be stored on disk as a serialized
 * tree. Maybe??
 */
void init_filesystem();



int open_file(superblock_t *superblock, open_file_table_t *open_file_table, char *path);
int close_file(superblock_t *superblock, open_file_table_t *open_file_table, int file_descriptor);

int read_file(inode_t *inode, void *buffer, unsigned short offset, unsigned short size);
int write_file(superblock_t *superblock, inode_t *inode, void *buffer, unsigned short offset, unsigned short size);

int create_file(superblock_t *superblock, int type, char *file_path, short major, short minor);
int delete_file(superblock_t *superblock, open_file_table_t *open_file_table, char *file_path);


#endif