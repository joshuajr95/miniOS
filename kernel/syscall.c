

#include "syscall.h"
#include "ktypes.h"
#include "task.h"
#include "filesystem.h"


extern task_table_t task_table;
extern superblock_t *ramdisk_superblock;
extern open_file_table_t open_file_table; 



/*
 * System call table implementation. This stores the
 * handler function for each system call. Since each
 * system call may have different parameter types and
 * even different numbers of parameters, it is difficult
 * (or impossible) to declare the syscall table using function
 * pointers. Thus, each handler function is cast to a void *
 * pointer before being inserted into the system call table.
 * As long as the system call/function call ABI is not interfered
 * with, this typecasting should not affect the working of
 * these functions. For example, in MIPS, the system call
 * wrapper functions will load the arguments to the system call
 * into the a0-a3 registers, and the system call number into v0.
 * The system call dispatch code will use v0 to select the correct
 * handler function, and the handler function will use the a0-a3
 * registers for arguments to the function. As long as the syscall
 * dispatch code does not modify the a0-a3 registers and the syscall
 * handler function has the same number and type of arguments as the
 * syscall userspace wrapper function, the ABI is unchanged and should
 * work properly.
 */
void *syscall_table[] = {
    [SYSCALL_CODE_CREATE_TASK]  = __SYSCALL_TABLE__ do_syscall_create_task,
    [SYSCALL_CODE_KILL_TASK]    = __SYSCALL_TABLE__ do_syscall_kill_task,
    [SYSCALL_CODE_YIELD]        = __SYSCALL_TABLE__ do_syscall_yield,
    [SYSCALL_CODE_WAIT]         = __SYSCALL_TABLE__ do_syscall_wait,
    [SYSCALL_CODE_WAITPID]      = __SYSCALL_TABLE__ do_syscall_waitpid,
    [SYSCALL_CODE_EXIT]         = __SYSCALL_TABLE__ do_syscall_exit,
    [SYSCALL_CODE_OPEN]         = __SYSCALL_TABLE__ do_syscall_open,
    [SYSCALL_CODE_CLOSE]        = __SYSCALL_TABLE__ do_syscall_close,
    [SYSCALL_CODE_READ]         = __SYSCALL_TABLE__ do_syscall_read,
    [SYSCALL_CODE_WRITE]        = __SYSCALL_TABLE__ do_syscall_write,
    [SYSCALL_CODE_MKFILE]       = __SYSCALL_TABLE__ do_syscall_mkfile,
    [SYSCALL_CODE_SEEK]         = __SYSCALL_TABLE__ do_syscall_seek,
    [SYSCALL_CODE_MKDIR]        = __SYSCALL_TABLE__ do_syscall_mkdir,
    [SYSCALL_CODE_DELETE_FILE]  = __SYSCALL_TABLE__ do_syscall_delete_file
};





taskid_t do_syscall_create_task(void *function)
{
    taskid_t current_task_id = get_current_task(&task_table);
    taskid_t child_task_id = create_task(&task_table, current_task_id, function);
    schedule_next_task(&task_table);

    // store return value from syscall into task context
    set_task_register_value(&task_table, current_task_id, REGISTER_V0, child_task_id);

    return child_task_id;
}


int do_syscall_kill_task(taskid_t task_id)
{
    // TODO
}


int do_syscall_yield()
{
    // TODO
}

int do_syscall_wait()
{
    // TODO
}


int do_syscall_waitpid(int pid)
{
    // TODO
}


int do_syscall_exit()
{
    // TODO
}



int do_syscall_open(char *path)
{
    return open_file(ramdisk_superblock, task_table.current_task->current_directory, &open_file_table, path);
}


int do_syscall_close(int file_descriptor)
{
    if(is_open_file_free(&open_file_table, file_descriptor))
    {
        return -1;
    }

    close_file(ramdisk_superblock, &open_file_table, file_descriptor);

    return 0;
}



int do_syscall_read(int file_descriptor, void *buffer, int size)
{
    int bytes_read;

    if(is_open_file_free(&open_file_table, file_descriptor))
    {
        return -1;
    }

    inode_number_t inode_number = open_file_table.open_files[file_descriptor].inode_number;
    inode_t *inode_table = GET_POINTER_FROM_BLOCK_NUMBER(ramdisk_superblock->inode_table_start);
    inode_t *file_inode = &inode_table[inode_number];

    bytes_read = read_file(file_inode, buffer, open_file_table.open_files[file_descriptor].cursor, size);
    open_file_table.open_files[file_descriptor].cursor += bytes_read;

    return bytes_read;
}



int do_syscall_write(int file_descriptor, void *buffer, int size)
{
    int bytes_written;

    if(is_open_file_free(&open_file_table, file_descriptor))
    {
        return -1;
    }

    inode_number_t inode_number = open_file_table.open_files[file_descriptor].inode_number;
    inode_t *inode_table = GET_POINTER_FROM_BLOCK_NUMBER(ramdisk_superblock->inode_table_start);
    inode_t *file_inode = &inode_table[inode_number];

    bytes_written = write_file(ramdisk_superblock, file_inode, buffer, open_file_table.open_files[file_descriptor].cursor, size);
    open_file_table.open_files[file_descriptor].cursor += bytes_written;

    return bytes_written;
}



void do_syscall_seek(int file_descriptor, int offset)
{
    if(is_open_file_free(&open_file_table, file_descriptor))
    {
        return -1;
    }

    open_file_table.open_files[file_descriptor].cursor = offset;
}


void do_syscall_mkfile(char *path)
{
    if(path[0] == '/')
    {
        create_file(ramdisk_superblock, INODE_NONE, FILE_TYPE_REGULAR, path, 0, 0);
    }
    else
    {
        create_file(ramdisk_superblock, task_table.current_task->current_directory, FILE_TYPE_REGULAR, path, 0, 0);
    }
    
}


void do_syscall_mkdir(char *path)
{
    if(path[0] == '/')
    {
        create_file(ramdisk_superblock, INODE_NONE, FILE_TYPE_DIRECTORY, path, 0, 0);
    }
    else
    {
        create_file(ramdisk_superblock, task_table.current_task->current_directory, FILE_TYPE_DIRECTORY, path, 0, 0);
    }
}


void do_syscall_delete_file(char *path)
{
    if(path[0] == '/')
    {
        delete_file(ramdisk_superblock, INODE_NONE, &open_file_table, path);
    }
    else
    {
        delete_file(ramdisk_superblock, task_table.current_task->current_directory, &open_file_table, path);
    }
}

// TODO: Remaining syscalls

