
#include "fs_archive.h"




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


int unpack_filesystem_archive(filesystem_archive_t *archive)
{

}