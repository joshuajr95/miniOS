#ifndef FS_ARCHIVE_H
#define FS_ARCHIVE_H


#define RECORD_TYPE_FILE            0
#define RECORD_TYPE_DIRECTORY       1
#define RECORD_TYPE_LIST_END        2

typedef struct ARCHIVE
{
    int type;
    int has_children;
    char name[16];

} filesystem_archive_t;



int unpack_filesystem_archive(filesystem_archive_t *archive);


#endif
