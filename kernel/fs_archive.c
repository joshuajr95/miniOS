
#include "fs_archive.h"
#include "stdlib.h"
#include "filesystem.h"


extern superblock_t *ramdisk_superblock;



filesystem_archive_t __attribute__((section(".fs_archive"))) fs_archive[] = {
    {
        RECORD_TYPE_DIRECTORY,
        1,
        "root"
    },
    {
        RECORD_TYPE_DIRECTORY,
        0,
        "log"
    },
    {
        RECORD_TYPE_DIRECTORY,
        0,
        "tmp"
    },
    {
        RECORD_TYPE_DIRECTORY,
        0,
        "dev"
    },
    {
        RECORD_TYPE_LIST_END,
        0,
        ""
    }
};


static int unpack_directory_archive(filesystem_archive_t *current_record, inode_number_t *current_inode, int *current_level)
{
    inode_number_t new_inode = create_file(ramdisk_superblock, *current_inode, FILE_TYPE_DIRECTORY, current_record->name, 0, 0);

    if(current_record->has_children)
    {
        (*current_level)++;
        *current_inode = new_inode;
    }

    return 0;
}


static int unpack_file_archive(filesystem_archive_t *current_record, inode_number_t current_inode)
{
    create_file(ramdisk_superblock, current_inode, FILE_TYPE_REGULAR, current_record->name, 0, 0);

    return 0;
}


int unpack_filesystem_archive(filesystem_archive_t *archive)
{
    int current_level = 0;
    int current_index = 0;
    inode_number_t current_inode;
    filesystem_archive_t *current_record = &archive[current_index];
    
    if(!string_compare(current_record->name, "root", 6))
        return 0;
    
    create_root();
    current_inode = ramdisk_superblock->root_inode_index;

    // error checking
    if(!current_record->has_children)
    {
        return ARCHIVE_ERROR_NO_CHILD;
    }

    if(current_record->type != RECORD_TYPE_DIRECTORY)
    {
        return ARCHIVE_ERROR_WRONG_RECORD_TYPE;
    }

    current_level++;
    current_index++;
    current_record = &archive[current_index];

    while(!((current_level <= 0) && (current_record->type == RECORD_TYPE_LIST_END)))
    {
        switch (current_record->type)
        {
        case RECORD_TYPE_DIRECTORY:
            unpack_directory_archive(current_record, current_inode, &current_level);
            break;
        
        case RECORD_TYPE_FILE:
            unpack_file_archive(current_record, current_inode);
        
        case RECORD_TYPE_LIST_END:
            current_level--;
        
        default:
            break;
        }

        current_index++;
    }
}