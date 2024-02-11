
#ifndef KHEAP_H
#define KHEAP_H


/*
 * At some point in the future, I think
 * this should be changed to be more
 * configurable.
 */

#define BLOCKSIZE_32_BYTES 32       // 32
#define BLOCKSIZE_128_BYTES 128     // 24
#define BLOCKSIZE_512_BYTES 512     // 8


typedef struct HEAP_CONTROL_BLOCK
{
    /*
     * The following three variables
     * are bitmasks that keep track of
     * which blocks are allocated and
     * which are not. A given block is
     * allocated if the corresponding bit
     * is a 1 and free if it is 0.
     */
    unsigned int in_use_32B;
    unsigned int in_use_128B;
    unsigned char in_use_512B;

    int num_32B_blocks;
    int num_128B_blocks;
    int num_512B_blocks;

} heap_cb_t;



/*
 * Bitmask manipulation macros. Use bitwise OR mask to set
 * a given bit corresponding to a block number.
 */
#define SET_32B_BLOCK_IN_USE(_heap_cb, _block_number)       \
        if(_block_number < _heap_cb->num_32B_blocks)        \
        {                                                   \
            unsigned int mask = 0x1 << _block_number;       \
            _heap_cb->in_use_32B |= mask;                   \
        }

#define SET_128B_BLOCK_IN_USE(_heap_cb, _block_number)      \
        if(_block_number < _heap_cb->num_128B_blocks)       \
        {                                                   \
            unsigned int mask = 0x1 << _block_number;       \
            _heap_cb->in_use_128B |= mask;                  \
        }


#define SET_512B_BLOCK_IN_USE(_heap_cb, _block_number)      \
        if(_block_number < _heap_cb->num_512B_blocks)       \
        {                                                   \
            unsigned char mask = 0x1 << _block_number;      \
            _heap_cb->in_use_512B |= mask;                  \
        }



/*
 * Bitmask manipulation macros. Use bitwise AND mask to clear
 * a given bit corresponding to a block number.
 */
#define SET_32B_BLOCK_FREE(_heap_cb, _block_number)         \
        if(_block_number < _heap_cb->num_32B_blocks)        \
        {                                                   \
            unsigned int mask = ~(0x1 << _block_number);    \
            _heap_cb->in_use_32B &= mask;                   \
        }

#define SET_128B_BLOCK_FREE(_heap_cb, _block_number)        \
        if(_block_number < _heap_cb->num_128B_blocks)       \
        {                                                   \
            unsigned int mask = ~(0x1 << _block_number);    \
            _heap_cb->in_use_128B &= mask;                  \
        }


#define SET_512B_BLOCK_FREE(_heap_cb, _block_number)        \
        if(_block_number < _heap_cb->num_512B_blocks)       \
        {                                                   \
            unsigned char mask = ~(0x1 << _block_number);   \
            _heap_cb->in_use_512B &= mask;                  \
        }



/*
 * The following macros check whether a given block is in use.
 * Since these macros must "return" a value, they use a GNU
 * extension called statement expressions, which use an opening
 * and closing parentheses and curly braces to define the
 * expression. To use these, the __extension__ attribute must
 * be used.
 */
#define IS_32B_BLOCK_IN_USE(_heap_cb, _block_number)                    \
    __extension__ ({                                                    \
        int in_use;                                                     \
        if(_block_number < _heap_cb->num_32B_blocks)                    \
        {                                                               \
            unsigned int mask = 0x1 << _block_number;                   \
            in_use = (_heap_cb->in_use_32B & mask) >> _block_number;    \
        }                                                               \
        else                                                            \
        {                                                               \
            in_use = 0;                                                 \
        }                                                               \
        in_use;                                                         \
    })


#define IS_128B_BLOCK_IN_USE(_heap_cb, _block_number)                   \
    __extension__ ({                                                    \
        int in_use;                                                     \
        if(_block_number < _heap_cb->num_128B_blocks)                   \
        {                                                               \
            unsigned int mask = 0x1 << _block_number;                   \
            in_use = (_heap_cb->in_use_128B & mask) >> _block_number;   \
        }                                                               \
        else                                                            \
        {                                                               \
            in_use = 0;                                                 \
        }                                                               \
        in_use;                                                         \
    })


#define IS_512B_BLOCK_IN_USE(_heap_cb, _block_number)                   \
    __extension__ ({                                                    \
        int in_use;                                                     \
        if(_block_number < _heap_cb->num_512B_blocks)                   \
        {                                                               \
            unsigned int mask = 0x1 << _block_number;                   \
            in_use = (_heap_cb->in_use_512B & mask) >> _block_number;   \
        }                                                               \
        else                                                            \
        {                                                               \
            in_use = 0;                                                 \
        }                                                               \
        in_use;                                                         \
    })



/*
 * Macros to convert between block numbers and memory addresses.
 */
#define ADDRESS_OF_32B_BLOCK(_heap_cb, _block_number)                   \
    __extension__ ({                                                    \
        void *addr = kernel_heap_base;                                  \
        addr += _block_number*BLOCKSIZE_32_BYTES;                       \
        addr;                                                           \
    })

#define ADDRESS_OF_128B_BLOCK(_heap_cb, _block_number)                  \
    __extension__ ({                                                    \
        void *addr = kernel_heap_base;                                  \
        addr += _heap_cb->num_32B_blocks*BLOCKSIZE_32_BYTES;            \
        addr += _block_number*BLOCKSIZE_128_BYTES;                      \
        addr;                                                           \
    })

#define ADDRESS_OF_512B_BLOCK(_heap_cb, _block_number)                  \
    __extension__ ({                                                    \
        void *addr = kernel_heap_base;                                  \
        addr += _heap_cb->num_32B_blocks*BLOCKSIZE_32_BYTES;            \
        addr += _heap_cb->num_128B_blocks*BLOCKSIZE_128_BYTES;          \
        addr += _block_number*BLOCKSIZE_512_BYTES;                      \
        addr;                                                           \
    })



#define GET_NEXT_FREE_32B_BLOCK(_heap_cb)                               \
    __extension__ ({                                                    \
        void *ret = NULL_POINTER;                                       \
        int block_number = 0;                                           \
        while(block_number < _heap_cb->num_32B_blocks)                  \
        {                                                               \
            if(!IS_32B_BLOCK_IN_USE(_heap_cb, block_number))            \
            {                                                           \
                SET_32B_BLOCK_IN_USE(_heap_cb, block_number);           \
                ret = ADDRESS_OF_32B_BLOCK(_heap_cb, block_number);     \
                break;                                                  \
            }                                                           \
            block_number++;                                             \
        }                                                               \
        ret;                                                            \
    })


#define GET_NEXT_FREE_128B_BLOCK(_heap_cb)                              \
    __extension__ ({                                                    \
        void *ret = NULL_POINTER;                                       \
        int block_number = 0;                                           \
        while(block_number < _heap_cb->num_128B_blocks)                 \
        {                                                               \
            if(!IS_128B_BLOCK_IN_USE(_heap_cb, block_number))           \
            {                                                           \
                SET_128B_BLOCK_IN_USE(_heap_cb, block_number);          \
                ret = ADDRESS_OF_128B_BLOCK(_heap_cb, block_number);    \
                break;                                                  \
            }                                                           \
            block_number++;                                             \
        }                                                               \
        ret;                                                            \
    })


#define GET_NEXT_FREE_512B_BLOCK(_heap_cb)                              \
    __extension__ ({                                                    \
        void *ret = NULL_POINTER;                                       \
        int block_number = 0;                                           \
        while(block_number < _heap_cb->num_512B_blocks)                 \
        {                                                               \
            if(!IS_512B_BLOCK_IN_USE(_heap_cb, block_number))           \
            {                                                           \
                SET_512B_BLOCK_IN_USE(_heap_cb, block_number);          \
                ret = ADDRESS_OF_512B_BLOCK(_heap_cb, block_number);    \
                break;                                                  \
            }                                                           \
            block_number++;                                             \
        }                                                               \
        ret;                                                            \
    })


/*
 * Gets the blocksize from the address of the
 * memory. Useful for freeing memory.
 */
#define GET_BLOCKSIZE_FROM_POINTER(_heap_cb, _pointer)                  \
    __extension__ ({                                                    \
        int blocksize;                                                  \
        int offset = _pointer - kernel_heap_base;                       \
        if(offset < 0)                                                  \
        {                                                               \
            blocksize = 0;                                              \
        }                                                               \
        else if(offset < _heap_cb->num_32B_blocks*BLOCKSIZE_32_BYTES)   \
        {                                                               \
            blocksize = BLOCKSIZE_32_BYTES;                             \
        }                                                               \
        else if(offset < _heap_cb->num_128B_blocks*BLOCKSIZE_128_BYTES) \
        {                                                               \
            blocksize = BLOCKSIZE_128_BYTES;                            \
        }                                                               \
        else if(offset < _heap_cb->num_512B_blocks*BLOCKSIZE_512_BYTES) \
        {                                                               \
            blocksize = BLOCKSIZE_512_BYTES;                            \
        }                                                               \
        else                                                            \
        {                                                               \
            blocksize = 0;                                              \
        }                                                               \
        blocksize;                                                      \
    })



/*
 * Get the block number from an allocated pointer.
 */
#define GET_32B_BLOCKNUMBER_FROM_POINTER(_heap_cb, _pointer)            \
    __extension__ ({                                                    \
        int offset = _pointer - kernel_heap_base;                       \
        int block_number = offset / BLOCKSIZE_32_BYTES;                 \
        block_number;                                                   \
    })


#define GET_128B_BLOCKNUMBER_FROM_POINTER(_heap_cb, _pointer)           \
    __extension__ ({                                                    \
        int offset = _pointer - kernel_heap_base;                       \
        offset -= _heap_cb->num_32B_blocks*BLOCKSIZE_32_BYTES;          \
        int block_number = offset / BLOCKSIZE_128_BYTES;                \
        block_number;                                                   \
    })


#define GET_512B_BLOCKNUMBER_FROM_POINTER(_heap_cb, _pointer)           \
    __extension__ ({                                                    \
        int offset = _pointer - kernel_heap_base;                       \
        offset -= _heap_cb->num_32B_blocks*BLOCKSIZE_32_BYTES;          \
        offset -= _heap_cb->num_128B_blocks*BLOCKSIZE_128_BYTES;        \
        int block_number = offset / BLOCKSIZE_512_BYTES;                \
        block_number;                                                   \
    })



/*
 * Initializes the heap block allocator.
 * This will be called by the kernel initialization
 * procedures at startup.
 */
void init_heap(heap_cb_t *heap);


/*
 * Allocates a given number of bytes of memory
 * from the heap blocks. This is roughly equivalent
 * to malloc in the C standard library.
 */
void *allocate_memory(unsigned int num_bytes);


/*
 * Frees memory that is already allocated. This
 * is equivalent to free in C standard library.
 */
void free_memory(void *mem_to_free);


/*
 * This function is used to check whether or not
 * a given piece of memory is allocated or not.
 * This has no equivalent in C standard library
 * but is used to prevent use-after-free and
 * double-free errors.
 */
int is_allocated(void *mem_pointer);



#endif