

#include "kheap.h"
#include "kdefs.h"



extern heap_cb_t kernel_heap_cb;
extern void *kernel_heap_base;


void init_heap(heap_cb_t *heap)
{
    heap->in_use_32B = 0;
    heap->in_use_128B = 0;
    heap->in_use_512B = 0;

    heap->num_32B_blocks = 32;
    heap->num_128B_blocks = 24;
    heap->num_512B_blocks = 8;
}




void *allocate_memory(unsigned int num_bytes)
{
    void *mem_ptr;

    if(num_bytes <= BLOCKSIZE_32_BYTES)
    {
        mem_ptr = GET_NEXT_FREE_32B_BLOCK((&kernel_heap_cb));
    }

    else if(num_bytes <= BLOCKSIZE_128_BYTES)
    {
        mem_ptr = GET_NEXT_FREE_128B_BLOCK((&kernel_heap_cb));
    }

    else if(num_bytes <= BLOCKSIZE_512_BYTES)
    {
        mem_ptr = GET_NEXT_FREE_512B_BLOCK((&kernel_heap_cb));
    }
    
    else
    {
        mem_ptr = NULL_POINTER;
    }

    return mem_ptr;
}


void free_memory(void *mem_to_free)
{
    int blocksize = GET_BLOCKSIZE_FROM_POINTER((&kernel_heap_cb), mem_to_free);
    int blocknumber;

    if(blocksize == 0) return;

    switch (blocksize)
    {
    case BLOCKSIZE_32_BYTES:
        blocknumber = GET_32B_BLOCKNUMBER_FROM_POINTER((&kernel_heap_cb), mem_to_free);
        SET_32B_BLOCK_FREE((&kernel_heap_cb), blocknumber);
        break;
    
    case BLOCKSIZE_128_BYTES:
        blocknumber = GET_128B_BLOCKNUMBER_FROM_POINTER((&kernel_heap_cb), mem_to_free);
        SET_128B_BLOCK_FREE((&kernel_heap_cb), blocknumber);
        break;
    
    case BLOCKSIZE_512_BYTES:
        blocknumber = GET_512B_BLOCKNUMBER_FROM_POINTER((&kernel_heap_cb), mem_to_free);
        SET_512B_BLOCK_FREE((&kernel_heap_cb), blocknumber);
        break;
    
    default:
        break;
    }
}


int is_allocated(void *mem_pointer)
{
    int blocksize = GET_BLOCKSIZE_FROM_POINTER((&kernel_heap_cb), mem_pointer);
    int blocknumber;
    int is_allocated;

    if(blocksize == 0) return;

    switch (blocksize)
    {
    case BLOCKSIZE_32_BYTES:
        blocknumber = GET_32B_BLOCKNUMBER_FROM_POINTER((&kernel_heap_cb), mem_pointer);
        is_allocated = IS_32B_BLOCK_IN_USE((&kernel_heap_cb), blocknumber);
        break;
    
    case BLOCKSIZE_128_BYTES:
        blocknumber = GET_128B_BLOCKNUMBER_FROM_POINTER((&kernel_heap_cb), mem_pointer);
        is_allocated = IS_128B_BLOCK_IN_USE((&kernel_heap_cb), blocknumber);
        break;
    
    case BLOCKSIZE_512_BYTES:
        blocknumber = GET_512B_BLOCKNUMBER_FROM_POINTER((&kernel_heap_cb), mem_pointer);
        is_allocated = IS_512B_BLOCK_IN_USE((&kernel_heap_cb), blocknumber);
        break;
    
    default:
        break;
    }

    return is_allocated;
}

