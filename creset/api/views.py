from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, F
from libcloud.base import DriverType, get_driver
from libcloud.storage.types import ContainerDoesNotExistError, ObjectDoesNotExistError
from rest_framework import generics, filters, status
from rest_framework.exceptions import ParseError, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework_csv.renderers import CSVRenderer

from .filters import DocumentFilter
from .models import Project, Label, Document,qaDatasetAnnotation
from .permissions import IsAdminUserAndWriteOnly, IsProjectUser, IsOwnAnnotation
from .serializers import ProjectSerializer, LabelSerializer, DocumentSerializer, UserSerializer,qaDatasetAnnotationSerializer
from .serializers import ProjectPolymorphicSerializer
from .utils import CSVParser, ExcelParser, JSONParser, PlainTextParser, CoNLLParser, iterable_to_io
from .utils import JSONLRenderer
from .utils import JSONPainter, CSVPainter
from .utils_file import PlainTextParser as PlainTextParser_file
from pythainlp.corpus.common import thai_words
from pythainlp.tokenize import dict_trie
from pythainlp.tag.named_entity import ThaiNameTagger
from pythainlp import sent_tokenize, word_tokenize
from pythainlp.summarize import summarize
import random
import math

class Me(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class Features(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response({
            'cloud_upload': bool(settings.CLOUD_BROWSER_APACHE_LIBCLOUD_PROVIDER),
        })


class ProjectList(generics.ListCreateAPIView):
    serializer_class = ProjectPolymorphicSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated, IsAdminUserAndWriteOnly)

    def get_queryset(self):
        return self.request.user.projects

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_url_kwarg = 'project_id'
    #permission_classes = (IsAuthenticated, IsProjectUser, IsAdminUserAndWriteOnly)
    permission_classes = (IsAuthenticated, IsAdminUserAndWriteOnly)

class StatisticsAPI(APIView):
    pagination_class = None
    permission_classes = (IsAuthenticated, IsProjectUser, IsAdminUserAndWriteOnly)

    def get(self, request, *args, **kwargs):
        p = get_object_or_404(Project, pk=self.kwargs['project_id'])
        label_count, user_count = self.label_per_data(p)
        progress = self.progress(project=p)
        response = dict()
        response['label'] = label_count
        response['user'] = user_count
        response.update(progress)
        return Response(response)

    def progress(self, project):
        docs = project.documents
        annotation_class = project.get_annotation_class()
        total = docs.count()
        done = annotation_class.objects.filter(document_id__in=docs.all(),
            user_id=self.request.user).\
            aggregate(Count('document', distinct=True))['document__count']
        remaining = total - done
        return {'total': total, 'remaining': remaining}

    def label_per_data(self, project):
        annotation_class = project.get_annotation_class()
        return annotation_class.objects.get_label_per_data(project=project)


class ApproveLabelsAPI(APIView):
    permission_classes = (IsAuthenticated, IsProjectUser, IsAdminUser)

    def post(self, request, *args, **kwargs):
        approved = self.request.data.get('approved', True)
        document = get_object_or_404(Document, pk=self.kwargs['doc_id'])
        document.annotations_approved_by = self.request.user if approved else None
        document.save()
        return Response(DocumentSerializer(document).data)


class addTeamProject(APIView):
    permission_classes = (IsAuthenticated, IsProjectUser)

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])

        project.users.add(str(self.kwargs['team_project_id']))
        project.save()
        return Response(ProjectSerializer(project).data)
    
    '''def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        project.create(users='4')
        project.save()
        return Response(ProjectSerializer(Project).data)'''
    

class LabelList(generics.ListCreateAPIView):
    serializer_class = LabelSerializer
    pagination_class = None
    #permission_classes = (IsAuthenticated, IsProjectUser, IsAdminUserAndWriteOnly)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return project.labels

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        serializer.save(project=project)


class LabelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    lookup_url_kwarg = 'label_id'
    #permission_classes = (IsAuthenticated, IsProjectUser, IsAdminUserAndWriteOnly)
    permission_classes = (IsAuthenticated,)

class DocumentList(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('text', )
    ordering_fields = ('created_at', 'updated_at', 'doc_annotations__updated_at',
                       'seq_annotations__updated_at', 'seq2seq_annotations__updated_at')
    filter_class = DocumentFilter
    #permission_classes = (IsAuthenticated, IsProjectUser, IsAdminUserAndWriteOnly)
    permission_classes = (IsAuthenticated, IsAdminUserAndWriteOnly)
    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])

        queryset = project.documents

        if project.randomize_document_order:
            queryset = queryset.annotate(sort_id=F('id') % self.request.user.id).order_by('sort_id')
        
        return queryset

    def perform_create(self, serializer):
        if(IsProjectUser==True):
            project = get_object_or_404(Project, pk=self.kwargs['project_id'])
            serializer.save(project=project)


class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    lookup_url_kwarg = 'doc_id'
    #permission_classes = (IsAuthenticated, IsProjectUser, IsAdminUserAndWriteOnly)
    permission_classes = (IsAuthenticated, IsAdminUserAndWriteOnly)

class AnnotationList(generics.ListCreateAPIView):
    pagination_class = None
    permission_classes = (IsAuthenticated, IsProjectUser)
    #permission_classes = (IsAuthenticated,)
  
    def post(self, request, *args, **kwargs):
        # {'question': '11111111111111111111', 'answer': 'ทีมตน', 'start_answer': 573, 'end_answer': 578}
        return self.create(request, *args, **kwargs)
        

    
    def get_serializer_class(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        self.serializer_class = project.get_annotation_serializer()
        return self.serializer_class

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        model = project.get_annotation_class()

        queryset = model.objects.filter(document=self.kwargs['doc_id'])
        if not project.collaborative_annotation:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def create(self, request, *args, **kwargs):
        request.data['document'] = self.kwargs['doc_id']
        return super().create(request, args, kwargs)

    def perform_create(self, serializer):
        doc = get_object_or_404(Document, pk=self.kwargs['doc_id'])
        serializer.save(document=doc, user=self.request.user)

class AnnotationList_forgen_qa(generics.ListCreateAPIView):
    pagination_class = None
    permission_classes = (IsAuthenticated, IsProjectUser)
    #permission_classes = (IsAuthenticated,)
  
    def post(self, request, *args, **kwargs):
        print('annotationrequest -----------------------------------------------------')
        print(request.data)
        

        # text = 'ต่อจากนั้นเสด็จพระราชดำเนินไปทรงศึกษาที่โรงเรียนมิลฟิลด์ เมืองสตรีท แคว้นซอมเมอร์เซท เมื่อเดือนกันยายน พ.ศ. 2509'
        # word = 'พ.ศ. 2509'
        text = request.data['question']
        word = request.data['answer']
        text = text.replace(word,'')

        sentence_cut = word_tokenize(text, engine="newmm")
        word_cut = word_tokenize(word, engine="newmm")
        rand_range_sent_start = random.randint(0,int((len(sentence_cut)-1)/4))
        rand_range_sent_end = (random.randint(int((len(sentence_cut)-1)/1.35),int((len(sentence_cut)-1))))
        print(sentence_cut)
        print('rand_range_sent_start'+str(rand_range_sent_start))
        print('rand_range_sent_end'+str(rand_range_sent_end))
        ner = ThaiNameTagger()
        word_tag = ner.get_ner(word)
        question = []
        if(word_tag[0][2]=="O"):
            question.append('')
            # question.append('เพราะอะไร')
        elif(word_tag[0][2]=="B-PERSON"):
            question.append('ใครที่')
        elif(word_tag[0][2]=="I-PERSON"):
            question.append('คนไหนที่')
        elif(word_tag[0][2]=="B-DATE"):
            question.append('วันใดที่')
        elif(word_tag[0][2]=="I-DATE"):
            question.append('เมื่อใดที่')
        elif(word_tag[0][2]=="B-LOCATION"):
            question.append('ที่ใดที่')
        elif(word_tag[0][2]=="I-LOCATION"):
            question.append('ที่ใดที่')
        elif(word_tag[0][2]=="B-TIME"):
            question.append('เวลาใดที่')
        elif(word_tag[0][2]=="I-TIME"):
            question.append('เวลาใดที่')
        elif(word_tag[0][2]=="B-LAW"):
            question.append('คืออะไร')
        elif(word_tag[0][2]=="I-LAW"):
            question.append('คืออะไร')
        elif(word_tag[0][2]=="B-ORGANIZATION"):
            question.append('ที่ใดที่')
        elif(word_tag[0][2]=="I-ORGANIZATION"):
            question.append('ที่ใดที่')
        for i in (sentence_cut[rand_range_sent_start:rand_range_sent_end]):
            question.append(i)
        if(word_tag[0][2]=="O"):
            question.append('อะไร')
        rand_question = ''
        if(len(summarize(text, n=2)) <= 1):
            print('simple gen')
            for i in question:
                rand_question = rand_question+i
        else:
            print('before text sumarize',text)
            text = summarize(text, n=2)
            print('text sumarize',text)
            text_temp = ''+question[0]
            for i in text :
                text_temp =text_temp + i
            rand_question =text_temp
        if(word_tag[0][2]=="O"):
            print('setgen because O word')
            rand_question=''
            # math.ceil(int((len(sentence_cut))/2.0))
            for i in (sentence_cut[:int(math.ceil(float((len(sentence_cut))/2.0)))+1]):
                rand_question = rand_question + i
            rand_question=rand_question+ 'อะไร'
        print('question is -->',rand_question)
        # print("sent_tokenize:", sent_tokenize(text))
        # sentence_cut = sent_tokenize(text)
        # word_cut = sent_tokenize(word)
        # print(int(len(sentence_cut)/2))
        # print(len(sentence_cut))
        # print(random.randint(int((len(sentence_cut)-1)/5),int((len(sentence_cut)-1)/1.3)))
        # rand_range_sent_start = random.randint(0,int((len(sentence_cut)-1)/4))
        # rand_range_sent_end = (random.randint(int((len(sentence_cut)-1)/4*3),int((len(sentence_cut)-1))))
        # print("rand_range_sent_start"+str(rand_range_sent_start))
        # print("rand_range_sent_end"+str(rand_range_sent_end))
        # print(sentence_cut[rand_range_sent_start:rand_range_sent_end])

        # ner = ThaiNameTagger()
        # name_tag = ner.get_ner(text)
        # word_tag = ner.get_ner(word)
        # all_tag = ['O', 'B-PERSON', 'I-PERSON', 'B-DATE', 'I-DATE', 'B-LOCATION', 'I-LOCATION', 'B-TIME', 'I-TIME', 'B-LAW', 'I-LAW', 'B-ORGANIZATION', 'I-ORGANIZATION']
        # print('wordtag'+word_tag[0][2])
        # for i in name_tag:
        #     if i[2] not in all_tag :
        #         all_tag.append(i[2])
        #     if(i[2] != 'O'):
        #         print(i)
        # print(all_tag)

        # print('------------------------------------------------------------------------')
        # question = []
        # if(word_tag[0][2]=="O"):
        #     question.append('ทำไม')
        # elif(word_tag[0][2]=="B-PERSON"):
        #     question.append('ใครที่')
        # elif(word_tag[0][2]=="I-PERSON"):
        #     question.append('ใครที่')
        # elif(word_tag[0][2]=="B-DATE"):
        #     question.append('วันใดที่')
        # elif(word_tag[0][2]=="I-DATE"):
        #     question.append('วันใดที่')
        # elif(word_tag[0][2]=="B-LOCATION"):
        #     question.append('สถาณที่ใดที่')
        # elif(word_tag[0][2]=="I-LOCATION"):
        #     question.append('สถาณที่ใดที่')
        # elif(word_tag[0][2]=="B-TIME"):
        #     question.append('เวลาใดที่')
        # elif(word_tag[0][2]=="I-TIME"):
        #     question.append('เวลาใดที่')
        # elif(word_tag[0][2]=="B-LAW"):
        #     question.append('คืออะไร')
        # elif(word_tag[0][2]=="I-LAW"):
        #     question.append('คืออะไร')
        # elif(word_tag[0][2]=="B-ORGANIZATION"):
        #     question.append('สถาณที่ใดที่')
        # elif(word_tag[0][2]=="I-ORGANIZATION"):
        #     question.append('สถาณที่ใดที่')



        # for i in (sentence_cut[rand_range_sent_start:rand_range_sent_end]):
        #     question.append(i)

        # rand_question = ''
        # for i in question:
        #     rand_question = rand_question+i
        # print('question is -->',rand_question)
        # rand_question = rand_question.replace(word,'')

        
        request.data['question'] = rand_question 
        # {'question': '11111111111111111111', 'answer': 'ทีมตน', 'start_answer': 573, 'end_answer': 578}
        return self.create(request, *args, **kwargs)
        

    
    def get_serializer_class(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        self.serializer_class = project.get_annotation_serializer()
        return self.serializer_class

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        model = project.get_annotation_class()

        queryset = model.objects.filter(document=self.kwargs['doc_id'])
        if not project.collaborative_annotation:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def create(self, request, *args, **kwargs):
        request.data['document'] = self.kwargs['doc_id']
        return super().create(request, args, kwargs)

    def perform_create(self, serializer):
        doc = get_object_or_404(Document, pk=self.kwargs['doc_id'])
        serializer.save(document=doc, user=self.request.user)


class AnnotationDetail(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'annotation_id'
    permission_classes = (IsAuthenticated, IsProjectUser)
    #permission_classes = (IsAuthenticated,)
    def get_serializer_class(self):
        if(IsProjectUser):
            project = get_object_or_404(Project, pk=self.kwargs['project_id'])
            self.serializer_class = project.get_annotation_serializer()
            return self.serializer_class

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        model = project.get_annotation_class()
        self.queryset = model.objects.all()
        return self.queryset


class TextUploadAPI(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = (IsAuthenticated, IsProjectUser, IsAdminUser)

    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            print('textuploadAPI  ----------------------------------------------------------')
            raise ParseError('Empty content')

        self.save_file(
            user=request.user,
            file=request.data['file'],
            file_format=request.data['format'],
            project_id=kwargs['project_id'],
        )

        return Response(status=status.HTTP_201_CREATED)

    @classmethod
    def save_file(cls, user, file, file_format, project_id):
        project = get_object_or_404(Project, pk=project_id)
        parser = cls.select_parser(file_format)
        data = parser.parse(file)
        storage = project.get_storage(data)
        storage.save(user)

    @classmethod
    def select_parser(cls, file_format):
        if file_format == 'plain':
            return PlainTextParser()
        elif file_format == 'csv':
            return CSVParser()
        elif file_format == 'json':
            return JSONParser()
        elif file_format == 'conll':
            return CoNLLParser()
        elif file_format == 'excel':
            return ExcelParser()
        else:
            raise ValidationError('format {} is invalid.'.format(file_format))

class TextUploadAPI_file(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = (IsAuthenticated, IsProjectUser, IsAdminUser)

    def post(self, request, *args, **kwargs):
        if 'file' not in request.data:
            print('textuploadAPI  ----------------------------------------------------------')
            raise ParseError('Empty content')

        self.save_file(
            user=request.user,
            file=request.data['file'],
            file_format=request.data['format'],
            project_id=kwargs['project_id'],
        )

        return Response(status=status.HTTP_201_CREATED)

    @classmethod
    def save_file(cls, user, file, file_format, project_id):
        project = get_object_or_404(Project, pk=project_id)
        parser = cls.select_parser(file_format)
        data = parser.parse(file)
        storage = project.get_storage(data)
        storage.save(user)

    @classmethod
    def select_parser(cls, file_format):
        if file_format == 'plain':
            return PlainTextParser_file()
        elif file_format == 'csv':
            return CSVParser()
        elif file_format == 'json':
            return JSONParser()
        elif file_format == 'conll':
            return CoNLLParser()
        elif file_format == 'excel':
            return ExcelParser()
        else:
            raise ValidationError('format {} is invalid.'.format(file_format))


class CloudUploadAPI(APIView):
    permission_classes = TextUploadAPI.permission_classes

    def get(self, request, *args, **kwargs):
        try:
            project_id = request.query_params['project_id']
            file_format = request.query_params['upload_format']
            cloud_container = request.query_params['container']
            cloud_object = request.query_params['object']
        except KeyError as ex:
            raise ValidationError('query parameter {} is missing'.format(ex))

        try:
            cloud_file = self.get_cloud_object_as_io(cloud_container, cloud_object)
        except ContainerDoesNotExistError:
            raise ValidationError('cloud container {} does not exist'.format(cloud_container))
        except ObjectDoesNotExistError:
            raise ValidationError('cloud object {} does not exist'.format(cloud_object))

        TextUploadAPI.save_file(
            user=request.user,
            file=cloud_file,
            file_format=file_format,
            project_id=project_id,
        )

        next_url = request.query_params.get('next')

        if next_url == 'about:blank':
            return Response(data='', content_type='text/plain', status=status.HTTP_201_CREATED)

        if next_url:
            return redirect(next_url)

        return Response(status=status.HTTP_201_CREATED)

    @classmethod
    def get_cloud_object_as_io(cls, container_name, object_name):
        provider = settings.CLOUD_BROWSER_APACHE_LIBCLOUD_PROVIDER.lower()
        account = settings.CLOUD_BROWSER_APACHE_LIBCLOUD_ACCOUNT
        key = settings.CLOUD_BROWSER_APACHE_LIBCLOUD_SECRET_KEY

        driver = get_driver(DriverType.STORAGE, provider)
        client = driver(account, key)

        cloud_container = client.get_container(container_name)
        cloud_object = cloud_container.get_object(object_name)

        return iterable_to_io(cloud_object.as_stream())


class TextDownloadAPI(APIView):
    permission_classes = (IsAuthenticated, IsProjectUser, IsAdminUser)
    renderer_classes = (CSVRenderer, JSONLRenderer)

    def get(self, request, *args, **kwargs):
        format = request.query_params.get('q')
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        documents = project.documents.all()
        painter = self.select_painter(format)
        # json1 format prints text labels while json format prints annotations with label ids
        # json1 format - "labels": [[0, 15, "PERSON"], ..]
        # json format - "annotations": [{"label": 5, "start_offset": 0, "end_offset": 2, "user": 1},..]
        if format == "json1":
            labels = project.labels.all()
            data = JSONPainter.paint_labels(documents, labels)
        else:
            data = painter.paint(documents)
        return Response(data)

    def select_painter(self, format):
        if format == 'csv':
            return CSVPainter()
        elif format == 'json' or format == "json1":
            return JSONPainter()
        else:
            raise ValidationError('format {} is invalid.'.format(format))
