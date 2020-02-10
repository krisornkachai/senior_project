import Vue from 'vue';
import qaDataset from '../components/qaDataset.vue';

Vue.use(require('vue-shortkey'));

new Vue({
  el: '#mail-app',

  components: { qaDataset },

  template: '<qaDataset />',
});
