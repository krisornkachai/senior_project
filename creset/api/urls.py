from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns

from .views import Me, Features
from .views import ProjectList, ProjectDetail
from .views import LabelList, LabelDetail, ApproveLabelsAPI,addTeamProject
from .views import DocumentList, DocumentDetail
from .views import AnnotationList, AnnotationDetail,AnnotationList_forgen_qa
from .views import TextUploadAPI, TextDownloadAPI, CloudUploadAPI,TextUploadAPI_file
from .views import StatisticsAPI



urlpatterns = [
    path('auth-token', obtain_auth_token),
    path('me', Me.as_view(), name='me'),
    path('features', Features.as_view(), name='features'),
    path('cloud-upload', CloudUploadAPI.as_view(), name='cloud_uploader'),
    path('projects', ProjectList.as_view(), name='project_list'),
    path('projects/<int:project_id>', ProjectDetail.as_view(), name='project_detail'),
    path('projects/<int:project_id>/statistics',
         StatisticsAPI.as_view(), name='statistics'),
    path('projects/<int:project_id>/labels',
         LabelList.as_view(), name='label_list'),
    path('projects/<int:project_id>/labels/<int:label_id>',
         LabelDetail.as_view(), name='label_detail'),
    path('projects/<int:project_id>/docs',
         DocumentList.as_view(), name='doc_list'),
    path('projects/<int:project_id>/docs/<int:doc_id>',
         DocumentDetail.as_view(), name='doc_detail'),
    path('projects/<int:project_id>/docs/<int:doc_id>/approve-labels',
         ApproveLabelsAPI.as_view(), name='approve_labels'),
    path('projects/<int:project_id>/docs/<int:doc_id>/annotations',
         AnnotationList.as_view(), name='annotation_list'),

    path('projects/<int:project_id>/docs/<int:doc_id>/annotations_forgen_qa',
         AnnotationList_forgen_qa.as_view(), name='annotation_list_forgen_qa'),

    path('projects/<int:project_id>/docs/<int:doc_id>/annotations/<int:annotation_id>',
         AnnotationDetail.as_view(), name='annotation_detail'),
    path('projects/<int:project_id>/docs/upload',
         TextUploadAPI.as_view(), name='doc_uploader'),
    path('projects/<int:project_id>/docs/upload_file',
         TextUploadAPI_file.as_view(), name='doc_uploader_file'),
    path('projects/<int:project_id>/docs/download',
         TextDownloadAPI.as_view(), name='doc_downloader'),
    path('projects/<int:project_id>/add_team_project/<int:team_project_id>',
         addTeamProject.as_view(), name='add_team_project'),
   
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'xml'])
