<template lang="pug">
extends ./annotation.pug

block annotation-area
  
  
  div.card

    

    div.card-content
      div.content.scrollable(v-if="docs[pageNumber] && annotations[pageNumber]", ref="textbox")
        annotator(
          v-bind:labels="labels"
          v-bind:entity-positions="annotations[pageNumber]"
          v-bind:search-query="searchQuery"
          v-bind:text="docs[pageNumber].text"
          v-on:remove-label="removeLabel"
          v-on:add-label="addLabel"
          v-on:add-label-gen="addLabel_gen"
          ref="annotator"
        )
  a.button.is-medium.is-warning(v-on:click="isActive = !isActive") switch mode
  a(v-if="!isActive").button.is-medium.is-primary(v-on:click="annotate()") manual add question
  a(v-if="isActive").button.is-medium.is-danger(v-on:click="annotate_gen()") auto add question

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
            label(v-on:dblclick="editTodo(todo)") คำถาม){{ todo.question }}
            button.delete.destroy.is-large(v-on:click="removeTodo(todo)")
            label(v-on:dblclick="editTodo(todo)") คำตอบ){{ todo.answer }}
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
    isActive: false,

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
    annotate_gen() {
      console.log('addlabel gen')
      this.$refs.annotator.addLabel_gen();
    },

    addLabel(annotation) {
      const docId = this.docs[this.pageNumber].id;
      console.log(annotation.start_offset);
      console.log(annotation.answer);
      const value = this.newTodo && this.newTodo.trim();
      if (!value) {
        return;
      }
      
     
      const payload = {
        question: value,
        answer: annotation.answer,
        start_answer: annotation.start_offset,
        end_answer: annotation.end_offset
      };
      HTTP.post(`docs/${docId}/annotations`, payload).then((response) => {
        this.annotations[this.pageNumber].push(response.data);
      });

      this.newTodo = '';

    },
     addLabel_gen(annotation) {
      const docId = this.docs[this.pageNumber].id;
      console.log(annotation.start_offset);
      console.log(annotation.answer);
      console.log('addlabel_gen')
      const payload = {
        question: annotation.answer_forgen,
        answer: annotation.answer,
        start_answer: annotation.start_offset,
        end_answer: annotation.end_offset
      };
      HTTP.post(`docs/${docId}/annotations_forgen_qa`, payload).then((response) => {
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
