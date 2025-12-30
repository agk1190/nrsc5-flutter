#pragma once

#define USE_FAAD2

#define HAVE_STRNDUP
#define HAVE_CMPLXF
/* #undef HAVE_IMAGINARY_I */
#define HAVE_COMPLEX_I

#ifndef HAVE_CMPLXF
#if (__GNUC__ > 4 || (__GNUC__ == 4 && __GNUC_MINOR__ >= 7))
    #define CMPLXF(x,y) __builtin_complex((float)(x), (float)(y))
#elif defined(HAVE_IMAGINARY_I)
    #define CMPLXF(x,y) ((float complex)((float)(x) + _Imaginary_I * (float)(y)))
#elif defined(HAVE_COMPLEX_I)
    #define CMPLXF(x,y) ((float complex)((float)(x) + _Complex_I * (float)(y)))
#endif
#endif /* HAVE_CMPLXF */

#define LIBRARY_DEBUG_LEVEL 5

#ifndef HAVE_STRNDUP
#include <stdlib.h>
char *strndup(char const *s, size_t n);
#endif
