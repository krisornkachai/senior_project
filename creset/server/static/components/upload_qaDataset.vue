<template lang="pug">
extends ./upload.pug

block select-format-area




block example-format-area
  pre.code-block(v-show="format === 'plain'")
    code.plaintext
      include ./examples/upload_seq2seq.txt
      | ...

</template>

<script>
import uploadMixin from './uploadMixin';

export default uploadMixin;
</script>
