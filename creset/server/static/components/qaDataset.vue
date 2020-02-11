<template lang="pug">
extends ./annotation.pug

block annotation-area
  div.card
    a.button(v-on:click="annotate()") addData
    

    div.card-content
      div.content.scrollable(v-if="docs[pageNumber] && annotations[pageNumber]", ref="textbox")
        annotator(
          v-bind:labels="labels"
          v-bind:entity-positions="annotations[pageNumber]"
          v-bind:search-query="searchQuery"
          v-bind:text="docs[pageNumber].text"
          v-on:remove-label="removeLabel"
          v-on:add-label="addLabel"
          ref="annotator"
        )


  section.todoapp
    header.header
      input.textarea.new-todo(
        v-model="newTodo"
        v-on:keyup.enter="addTodo"
        type="text"
        placeholder="What is your answer?"
      )

    section.main(v-cloak="")
      ul.todo-list
        li.todo(
          v-for="todo in annotations[pageNumber]"
          v-bind:key="todo.id"
          v-bind:class="{ editing: todo == editedTodo }"
        )
          div.view
            label(v-on:dblclick="editTodo(todo)") {{ todo.question }}
            button.delete.destroy.is-large(v-on:click="removeTodo(todo)")

          input.textarea.edit(
            v-model="todo.question"
            v-todo-focus="todo == editedTodo"
            v-on:blur="doneEdit(todo)"
            v-on:keyup.enter="doneEdit(todo)"
            v-on:keyup.esc="cancelEdit(todo)"
            type="text"
          )
</template>

<script>
import annotationMixin from './annotationMixin';
import todoFocus from './directives';
import HTTP from './http';
import Annotator from './annotator_qaDataset.vue';
import { simpleShortcut } from './filter';

export default {
  filters: { simpleShortcut },
  components: { Annotator },
  directives: { todoFocus },
  mixins: [annotationMixin],

  data: () => ({
    newTodo: '',
    editedTodo: null,
  }),

  methods: {
    addTodo() {
      const value = this.newTodo && this.newTodo.trim();
      if (!value) {
        return;
      }
      
      const docId = this.docs[this.pageNumber].id;
      const payload = {
        question: value,
        answer: "aaaaaa",
        start_answer: 14,
        end_answer: 15
      };
      HTTP.post(`docs/${docId}/annotations`, payload).then((response) => {
        this.annotations[this.pageNumber].push(response.data);
      });

      this.newTodo = '';
    },

    removeTodo(todo) {
      const docId = this.docs[this.pageNumber].id;
      HTTP.delete(`docs/${docId}/annotations/${todo.id}`).then(() => {
        const index = this.annotations[this.pageNumber].indexOf(todo);
        this.annotations[this.pageNumber].splice(index, 1);
      });
    },

    editTodo(todo) {
      this.beforeEditCache = todo.question;
      this.editedTodo = todo;
    },

    doneEdit(todo) {
      if (!this.editedTodo) {
        return;
      }
      this.editedTodo = null;
      todo.question = todo.question.trim();
      if (!todo.question) {
        this.removeTodo(todo);
      }
      const docId = this.docs[this.pageNumber].id;
      HTTP.put(`docs/${docId}/annotations/${todo.id}`, todo).then((response) => {
        console.log(response); // eslint-disable-line no-console
      });
    },

    cancelEdit(todo) {
      this.editedTodo = null;
      todo.question = this.beforeEditCache;
    },
    annotate() {
      //console.log(labelId)
      this.$refs.annotator.addLabel();
    },

    addLabel(annotation) {
      const docId = this.docs[this.pageNumber].id;
      console.log(annotation.start_offset);
      console.log(annotation.text);
      const value = this.newTodo && this.newTodo.trim();
      if (!value) {
        return;
      }
      
     
      const payload = {
        question: value,
        answer: "aaaaa",
        start_answer: annotation.start_offset,
        end_answer: annotation.end_offset
      };
      HTTP.post(`docs/${docId}/annotations`, payload).then((response) => {
        this.annotations[this.pageNumber].push(response.data);
      });

      this.newTodo = '';

    },

    async submit() {
      const state = this.getState();
      this.url = `docs?q=${this.searchQuery}&seq2seq_annotations__isnull=${state}&offset=${this.offset}`;
      await this.search();
      this.pageNumber = 0;
    },
  },
};
</script>
