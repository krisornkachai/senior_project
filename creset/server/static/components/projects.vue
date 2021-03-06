<template lang="pug">
  div(v-cloak="")
    //- section.hero.project-image
    //-   div.container
    //-     div.columns
    //-       div.column.is-10.is-offset-1
    //-         p(v-if="isSuperuser")
    //-           a.button.is-medium.is-primary(v-on:click="isActive = !isActive") Create Project
    section.hero.project-image
        div.container
          div.column.is-10.is-offset-1
            p(v-if="isSuperuser")
              a.button.is-medium.is-info(v-on:click="isActive = !isActive") Create Project

    div.modal(v-bind:class="{ 'is-active': isActive }")
      div.modal-background
      div.modal-card
        header.modal-card-head
          p.modal-card-title Create Project
          button.delete(aria-label="close", v-on:click="isActive = !isActive")
          

        section.modal-card-body
          div.field
            label.label Project Name
            div.control
              input.input(v-model="projectName", type="text", required, placeholder="Project name")
            p.help.is-danger {{ projectNameError }}

          div.field
            label.label Description
            div.control
              textarea.textarea(v-model="description", required, placeholder="Project description")
            p.help.is-danger {{ descriptionError }}

          div.field
            label.label Project Type

            div.control
              select(v-model="projectType", name="project_type", required)
                option(value="", selected="selected") ---------
                option(value="SequenceLabeling") word tagging
                option(value="Seq2seq") sentence classification
                option(value="DocumentClassification") document classification
                option(value="qaDataset") question answering dataset
            p.help.is-danger {{ projectTypeError }}

          div.field
            label.checkbox
              input(
                v-model="collaborativeAnnotation"
                name="collaborative_annotation"
                type="checkbox"
                style="margin-right: 0.25em;"
                required
              )
              | Share Project
       

        footer.modal-card-foot.pt20.pb20.pr20.pl20.has-background-white-ter
          button.button.is-primary(v-on:click="create()") Create
          button.button(v-on:click="isActive = !isActive") Cancel

    div.modal(v-bind:class="{ 'is-active': isDelete }")
      div.modal-background
      div.modal-card
        header.modal-card-head
          p.modal-card-title Delete Project
          button.delete(aria-label="close", v-on:click="isDelete = !isDelete")
        section.modal-card-body Are you sure you want to delete project?
        footer.modal-card-foot.pt20.pb20.pr20.pl20.has-background-white-ter
          button.button.is-danger(v-on:click="deleteProject()") Delete
          button.button(v-on:click="isDelete = !isDelete") Cancel
    section.hero
      div.container
        div.columns
          div.column.is-10.is-offset-1
            div.card.events-card
              header.card-header
                p.card-header-title {{ items.length }} Projects  [username : {{username}}][userid : {{user_id}}]
                

                div.field.card-header-icon
                  div.control
            

              div.card-table
                div.content
                  table.table.is-fullwidth
                    tbody
                      tr(v-for="project in selectedProjects", v-bind:key="project.id")
                        td.pl15r
                          div.thumbnail-wrapper.is-vertical
                            img.project-thumbnail(
                              v-bind:src="project.image"
                              alt="Project thumbnail"
                            )

                          div.dataset-item__main.is-vertical
                            div.dataset-item__main-title
                              div.dataset-item__main-title-link.dataset-item__link
                                a.has-text-black(v-bind:href="'/projects/' + project.id")
                                  | {{ project.name }} [project_id {{ project.id }}]

                            div.dataset-item__main-subtitle {{ project.description }}
                            div.dataset-item__main-info
                              span.dataset-item__main-update updated
                                span {{ project.updated_at | daysAgo }}

                        td.is-vertical
                          p(v-if="project.project_type =='SequenceLabeling'")
                            span.tag.is-normal {{ 'wold tagging' }}
                          p(v-if="project.project_type =='Seq2seq'")
                            span.tag.is-normal {{ 'sentence classification' }}
                          p(v-if="project.project_type =='DocumentClassification'")
                            span.tag.is-normal {{ 'document classification' }}
                          p(v-if="project.project_type =='qaDataset'")
                            span.tag.is-normal {{ 'question answering dataset' }}                            
                        td.is-vertical(v-if="isSuperuser")
                          a(v-bind:href="'/projects/' + project.id + '/docs'") manage project

                        td.is-vertical(v-if="isSuperuser")
                          a.button.is-medium.is-danger(v-on:click="setProject(project)") Delete
</template>

<script>
import { title, daysAgo } from './filter';
import { defaultHttpClient } from './http';

export default {
  filters: { title, daysAgo },

  data: () => ({
    items: [],
    isActive: false,
    isDelete: false,
    project: null,
    selected: 'All Project',
    projectName: '',
    description: '',
    projectType: '',
    projectType: '',
    projectType_name: '',
    descriptionError: '',
    projectTypeError: '',
    projectNameError: '',
    username: '',
    isSuperuser: false,
    randomizeDocumentOrder: false,
    collaborativeAnnotation: false,
    user_id:'',
  }),

  computed: {
    selectedProjects() {
      return this.items.filter(item => this.selected === 'All Project' || this.matchType(item.project_type));
    },
  },

  created() {
    Promise.all([
      defaultHttpClient.get('/v1/projects'),
      defaultHttpClient.get('/v1/me'),
    ]).then(([projects, me]) => {
      this.items = projects.data;
      this.username = me.data.username;
      this.isSuperuser = me.data.is_superuser;
      this.user_id = me.data.id;
    });
  },

  methods: {
    deleteProject() {
      defaultHttpClient.delete(`/v1/projects/${this.project.id}`).then(() => {
        this.isDelete = false;
        const index = this.items.indexOf(this.project);
        this.items.splice(index, 1);
      });
    },

    setProject(project) {
      this.project = project;
      this.isDelete = true;
    },

    matchType(projectType) {
      if (projectType === 'DocumentClassification') {
        return this.selected === 'Text Classification';
      }
      if (projectType === 'SequenceLabeling') {
        return this.selected === 'Sequence Labeling';
      }
      if (projectType === 'Seq2seq') {
        return this.selected === 'Seq2seq';
      }
      if (projectType === 'qaDataset') {
        return this.selected === 'qaDataset';
      }
      return false;
    },

    create() {
      const payload = {
        name: this.projectName,
        description: this.description,
        project_type: this.projectType,
        randomize_document_order: this.randomizeDocumentOrder,
        collaborative_annotation: this.collaborativeAnnotation,
        guideline: 'Please write annotation guideline.',
        resourcetype: this.resourceType(),
      };
      defaultHttpClient.post('/v1/projects', payload)
        .then((response) => {
          //window.location = `/projects/${response.data.id}/docs/create`;
          window.location = `/projects/`;
        })
        .catch((error) => {
          this.projectTypeError = '';
          this.projectNameError = '';
          this.descriptionError = '';
          if ('resourcetype' in error.response.data) {
            this.projectTypeError = error.response.data.resourcetype;
          }
          if ('name' in error.response.data) {
            this.projectNameError = error.response.data.name[0];
          }
          if ('description' in error.response.data) {
            this.descriptionError = error.response.data.description[0];
          }
        });
    },

    resourceType() {
      if (this.projectType === 'DocumentClassification') {
        return 'TextClassificationProject';
      }
      if (this.projectType === 'SequenceLabeling') {
        return 'SequenceLabelingProject';
      }
      if (this.projectType === 'Seq2seq') {
        return 'Seq2seqProject';
      }
       if (this.projectType === 'qaDataset') {
        return 'qaDatasetProject';
      }
      return '';
    },
  },
};
</script>
