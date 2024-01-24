

#ifndef KTYPES_H
#define KTYPES_H



/*
 * The Globally Unique Identifier (GUID)
 * type is used for unique identification of
 * various miniOS objects of different types.
 * This is useful when objects of different
 * types need to be treated similarly. For
 * example, registering an event handler that
 * will be triggered when a task exits, or one
 * that is triggered when a data packet arrives
 * both involve registering a callback function,
 * but the target object in one case is a task
 * and in the other is a network connection, which
 * are two very different types of objects.
 */
typedef unsigned int guid_t;


/*
 * Task ID type is used for keeping track of
 * different tasks.
 */
typedef int taskid_t;




#endif