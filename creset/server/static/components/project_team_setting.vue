<template lang="pug">
  div(v-cloak="")
    section.hero.project-image
      div.container
        div.columns
          div.column.is-10.is-offset-1

            
          



            p(v-if="isSuperuser")
              a.button.is-medium.is-primary(v-on:click="isActive = !isActive") add team project

    div.modal(v-bind:class="{ 'is-active': isActive }")
      div.modal-background
      div.modal-card
        header.modal-card-head
          p.modal-card-title add team project
          button.delete(aria-label="close", v-on:click="isActive = !isActive")

        section.modal-card-body
          div.field
            label.label Project id
            div.control
              input.input(v-model="project_id", type="text", required, placeholder="Project id for add team project")
            p.help.is-danger {{ projectNameError }}

          div.field
            label.label User id
            div.control
              input.input(v-model="user_id", required, placeholder="user id for add team project")
            p.help.is-danger {{ descriptionError }}


        footer.modal-card-foot.pt20.pb20.pr20.pl20.has-background-white-ter
          button.button.is-primary(v-on:click="create()") add
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
                p.card-header-title {{ items.length }} Projects

                div.field.card-header-icon
                  div.control
                    div.select
                      select(v-model="selected")
                        option(selected) All Project
                        option Text Classification
                        option Sequence Labeling
                        option Seq2seq

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
                                  | {{ project.name }}

                            div.dataset-item__main-subtitle {{ project.description }}
                            div.dataset-item__main-info
                              span.dataset-item__main-update updated
                                span {{ project.updated_at | daysAgo }}

                        td.is-vertical
                          span.tag.is-normal {{ project.project_type }}

                        td.is-vertical(v-if="isSuperuser")
                          a(v-on:click="addTeamProject(project)") add team

                        td.is-vertical(v-if="isSuperuser")
                          a(v-bind:href="'/projects/' + project.id + '/docs'") Edit

                        td.is-vertical(v-if="isSuperuser")
                          a.has-text-danger(v-on:click="setProject(project)") Delete
</template>

<script>
import { title, daysAgo } from './filter';
import { defaultHttpClient } from './http';

export default {
  filters: { title, daysAgo },

  data: () => ({
    project_id:'',
    user_id:'',
    items: [],
    isActive: false,
    isDelete: false,
    project: null,
    selected: 'All Project',
    projectName: '',
    description: '',
    projectType: '',
    descriptionError: '',
    projectTypeError: '',
    projectNameError: '',
    username: '',
    isSuperuser: false,
    randomizeDocumentOrder: false,
    collaborativeAnnotation: false,
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
    addTeamProject(project) {
      this.project = project;
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
        user_id: this.user_id,
        project_id: this.project_id,

      };
      defaultHttpClient.post(`/v1/projects/${this.project_id}/add_team_project/${this.user_id}`, payload)
      
        
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
