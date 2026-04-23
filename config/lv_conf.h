/**
 * @file lv_conf.h
 * Configuration file for v8.x
 */

#ifndef LV_CONF_H
#define LV_CONF_H

#include <stdint.h>

/* clang-format off */

#define LV_USE_LOG 1
#define LV_LOG_LEVEL LV_LOG_LEVEL_INFO

/* Memory management */
#define LV_MEM_CUSTOM 1
#if LV_MEM_CUSTOM
    #define LV_MEM_CUSTOM_INCLUDE "py/runtime.h"
    #define LV_MEM_CUSTOM_ALLOC   m_malloc
    #define LV_MEM_CUSTOM_FREE    m_free
    #define LV_MEM_CUSTOM_REALLOC m_realloc
#endif

/* Color depth: 1 (1 byte per pixel), 8 (RGB332), 16 (RGB565), 32 (ARGB8888) */
#define LV_COLOR_DEPTH 16

/* Example: enable some widgets */
#define LV_USE_BTN 1
#define LV_USE_LABEL 1

#endif /*LV_CONF_H*/
