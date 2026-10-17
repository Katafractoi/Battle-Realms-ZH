#include <stdint.h>
#include <string.h>
#include "blast.h"

struct output_state { unsigned char *data; unsigned used; unsigned cap; };
static unsigned no_input(void *unused, unsigned char **buf) { (void)unused; *buf = 0; return 0; }
static int bounded_output(void *ctx, unsigned char *buf, unsigned len) {
    struct output_state *s = (struct output_state *)ctx;
    if (len > s->cap - s->used) return 1;
    memcpy(s->data + s->used, buf, len);
    s->used += len;
    return 0;
}

__declspec(dllexport) int blast_buffer(const unsigned char *packed, unsigned packed_len,
                                       unsigned char *raw, unsigned raw_cap,
                                       unsigned *raw_len, unsigned *unused_len) {
    if (!packed || !raw || !raw_len || !unused_len || packed_len < 2 || raw_cap == 0) return -100;
    struct output_state s = {raw, 0, raw_cap};
    unsigned char *cursor = (unsigned char *)packed;
    unsigned left = packed_len;
    int result = blast(no_input, 0, bounded_output, &s, &left, &cursor);
    *raw_len = s.used;
    *unused_len = left;
    return result;
}
