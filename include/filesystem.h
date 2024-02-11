


#ifndef FILESYSTEM_H
#define FILESYSTEM_H


// in future make this configurable via kernel.cfg
#define MAX_FILENAME_LENGTH 16

#define MAX_DIRECTORY_ENTRIES 64

//  max blocks in a given file
#define MAX_BLOCKS 128

// maximum files on the whole system
#define MAX_FILES 512


// will make fully configurable later
#define BLOCK_SIZE 256

/*
 * Macros defining different file types.
 */
#define FILE_TYPE_REGULAR       0
#define FILE_TYPE_DIRECTORY     1
#define FILE_TYPE_CHAR          2
#define FILE_TYPE_BLOCK         3
#define FILE_TYPE_NET           4
#define FILE_TYPE_NONE          255


typedef short inode_number_t;
typedef short block_number_t;


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
    short file_type;
    short file_size;
    // permissions, timestamp, etc.
    block_number_t block_numbers[MAX_BLOCKS];

} inode_t;


typedef struct INODE_TABLE_ENTRY
{
    inode_number_t inode_number;
    block_number_t first_block_number;

} inode_table_entry_t;


typedef struct SUPERBLOCK
{
    /*
     * Block number of beginning of
     * inode table.
     */
    block_number_t inode_table_start;

    /*
     * Number of blocks occupied by 
     * the inode table.
     */
    unsigned short inode_table_num_blocks;

} superblock_t;



/*
 * Initial filesystem image will be stored on disk as a serialized
 * tree. Maybe??
 */
void init_filesystem();

#endif