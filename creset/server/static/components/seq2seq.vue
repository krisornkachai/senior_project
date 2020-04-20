// <template lang="pug">
// extends ./annotation.pug

// block annotation-area
//   div.card.has-text-weight-bold.has-text-white.has-background-royalblue
//     div.card-content
//       div.content(v-if="docs[pageNumber]")
//         span.text {{ docs[pageNumber].text }}

//   section.todoapp
//     header.header
//       input.textarea.new-todo(
//         v-model="newTodo"
//         v-on:keyup.enter="addTodo"
//         type="text"
//         placeholder="What is your answer?"
//       )

//     section.main(v-cloak="")
//       ul.todo-list
//         li.todo(
//           v-for="todo in annotations[pageNumber]"
//           v-bind:key="todo.id"
//           v-bind:class="{ editing: todo == editedTodo }"
//         )
//           div.view
//             label(v-on:dblclick="editTodo(todo)") {{ todo.text }}
//             button.delete.destroy.is-large(v-on:click="removeTodo(todo)")

//           input.textarea.edit(
//             v-model="todo.text"
//             v-todo-focus="todo == editedTodo"
//             v-on:blur="doneEdit(todo)"
//             v-on:keyup.enter="doneEdit(todo)"
//             v-on:keyup.esc="cancelEdit(todo)"
//             type="text"
//           )
// </template>

// <script>
// import annotationMixin from './annotationMixin';
// import todoFocus from './directives';
// import HTTP from './http';

// export default {
//   directives: { todoFocus },

//   mixins: [annotationMixin],

//   data: () => ({
//     newTodo: '',
//     editedTodo: null,
//   }),

//   methods: {
//     addTodo() {
//       const value = this.newTodo && this.newTodo.trim();
//       if (!value) {
//         return;
//       }
//       console.log('testtt'+this.docs[this.pageNumber].text);
//       const docId = this.docs[this.pageNumber].id;
//       const payload = {
//         text: value,
//         sentence:this.docs[this.pageNumber].text,
//       };
//       HTTP.post(`docs/${docId}/annotations`, payload).then((response) => {
//         this.annotations[this.pageNumber].push(response.data);
//       });

//       this.newTodo = '';
//     },

//     removeTodo(todo) {
//       const docId = this.docs[this.pageNumber].id;
//       HTTP.delete(`docs/${docId}/annotations/${todo.id}`).then(() => {
//         const index = this.annotations[this.pageNumber].indexOf(todo);
//         this.annotations[this.pageNumber].splice(index, 1);
//       });
//     },

//     editTodo(todo) {
//       this.beforeEditCache = todo.text;
//       this.editedTodo = todo;
//     },

//     doneEdit(todo) {
//       if (!this.editedTodo) {
//         return;
//       }
//       this.editedTodo = null;
//       todo.text = todo.text.trim();
//       if (!todo.text) {
//         this.removeTodo(todo);
//       }
//       const docId = this.docs[this.pageNumber].id;
//       HTTP.put(`docs/${docId}/annotations/${todo.id}`, todo).then((response) => {
//         console.log(response); // eslint-disable-line no-console
//       });
//     },

//     cancelEdit(todo) {
//       this.editedTodo = null;
//       todo.text = this.beforeEditCache;
//     },

//     async submit() {
//       const state = this.getState();
//       this.url = `docs?q=${this.searchQuery}&seq2seq_annotations__isnull=${state}&offset=${this.offset}`;
//       await this.search();
//       this.pageNumber = 0;
//     },
//   },
// };
// </script>

<template lang="pug">
extends ./annotation.pug

block annotation-area
  div.card
    header.card-header
      div.card-header-title.has-background-royalblue
        div.field.is-grouped.is-grouped-multiline
          div.control(v-for="label in labels")
            div.tags.has-addons
              a.tag.is-medium(
                v-shortkey.once="replaceNull(shortcutKey(label))"
                v-bind:style="{ \
                  color: label.text_color, \
                  backgroundColor: label.background_color \
                }"
                v-on:click="addLabel(label)"
                v-on:shortkey="addLabel(label)"
              ) {{ label.text }}
              span.tag.is-medium
                kbd {{ shortcutKey(label) | simpleShortcut }}

    div.card-content
      div.field.is-grouped.is-grouped-multiline
        div.control(v-for="annotation in annotations[pageNumber]")
          div.tags.has-addons(v-if="id2label[annotation.label]")
            span.tag.is-medium(
              v-bind:style="{ \
                color: id2label[annotation.label].text_color, \
                backgroundColor: id2label[annotation.label].background_color \
              }"
            ) {{ id2label[annotation.label].text }}
              button.delete.is-small(v-on:click="removeLabel(annotation)")

      hr
      div.content
        div.text.scrollable(ref="textbox", v-if="docs[pageNumber]") {{ docs[pageNumber].text }}
</template>

<style scoped>
hr {
  margin: 0.8rem 0;
}

.card-header-title {
  padding: 1.5rem;
}
</style>

<script>
import annotationMixin from './annotationMixin';
import HTTP from './http';
import { simpleShortcut } from './filter';

export default {
  filters: { simpleShortcut },

  mixins: [annotationMixin],

  methods: {
    getAnnotation(label) {
      return this.annotations[this.pageNumber].find(annotation => annotation.label === label.id);
    },

    async submit() {
      const state = this.getState();
      // this.url = `docs?q=${this.searchQuery}&doc_annotations__isnull=${state}&offset=${this.offset}`;
      this.url = `docs?q=${this.searchQuery}&seq2seq_annotations__isnull=${state}&offset=${this.offset}`;
      await this.search();
      this.pageNumber = 0;
    },

    async addLabel(label) {
      const annotation = this.getAnnotation(label);
      if (annotation) {
        this.removeLabel(annotation);
      } else {
        const docId = this.docs[this.pageNumber].id;
        const payload = {
          label: label.id,
          text:label.text,
          annotation_text:label.text
        };
        await HTTP.post(`docs/${docId}/annotations`, payload).then((response) => {
          this.annotations[this.pageNumber].push(response.data);
        });
      }
    },
  },
};
</script>

