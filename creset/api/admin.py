from django.contrib import admin

from .models import Label, Document, Project
from .models import DocumentAnnotation, SequenceAnnotation, Seq2seqAnnotation,qaDatasetAnnotation
from .models import TextClassificationProject, SequenceLabelingProject, Seq2seqProject,qaDatasetProject


class LabelAdmin(admin.ModelAdmin):
    list_display = ('text', 'project', 'text_color', 'background_color')
    ordering = ('project',)
    search_fields = ('project',)


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('text', 'project', 'meta')
    ordering = ('project',)
    search_fields = ('project',)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'project_type', 'randomize_document_order')
    ordering = ('project_type',)
    search_fields = ('name',)


class SequenceAnnotationAdmin(admin.ModelAdmin):
    list_display = ('document', 'label', 'start_offset', 'user')
    ordering = ('document',)
    search_fields = ('document',)


class DocumentAnnotationAdmin(admin.ModelAdmin):
    list_display = ('document', 'label', 'user')
    ordering = ('document',)
    search_fields = ('document',)


class Seq2seqAnnotationAdmin(admin.ModelAdmin):
    list_display = ('document', 'text', 'user')
    ordering = ('document',)
    search_fields = ('document',)

class qaDatasetAnnotationAdmin(admin.ModelAdmin):
    list_display = ('document', 'user','id', 'question','answer','start_question','end_question','start_answer','end_answer')
    ordering = ('document',)
    search_fields = ('document',)

admin.site.register(DocumentAnnotation, DocumentAnnotationAdmin)
admin.site.register(SequenceAnnotation, SequenceAnnotationAdmin)
admin.site.register(Seq2seqAnnotation, Seq2seqAnnotationAdmin)
admin.site.register(Label, LabelAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(TextClassificationProject, ProjectAdmin)
admin.site.register(SequenceLabelingProject, ProjectAdmin)
admin.site.register(Seq2seqProject, ProjectAdmin)
admin.site.register(qaDatasetProject, ProjectAdmin)
admin.site.register(qaDatasetAnnotation, qaDatasetAnnotationAdmin)