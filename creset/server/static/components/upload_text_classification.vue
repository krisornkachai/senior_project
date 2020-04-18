<template lang="pug">
extends ./upload.pug

block select-format-area
  

  label.radio
    input(
      type="radio"
      name="format"
      value="json"
      v-bind:checked="format == 'json'"
      v-model="format"
    )
    | JSONL



block example-format-area
  pre.code-block(v-show="format == 'plain'")
    code.plaintext
      include ./examples/upload_text_classification.txt
      | ...

 

  pre.code-block(v-show="format == 'json'")
    code.json
      include ./examples/upload_text_classification.jsonl
      | ...
</template>

<script>
import uploadMixin from './uploadMixin_file';

export default uploadMixin;
</script>
