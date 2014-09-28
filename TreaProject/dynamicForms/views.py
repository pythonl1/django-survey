
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.http import HttpResponse, Http404    
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max

from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import render_to_response
from dynamicForms.models import Form,FormEntry, Version, FieldEntry
from dynamicForms.fields import PUBLISHED, DRAFT
from dynamicForms.serializers import FormSerializer, UserSerializer
from dynamicForms.serializers import FieldEntrySerializer
from dynamicForms.serializers import VersionSerializer, FormEntrySerializer
from datetime import datetime
from django.http.response import HttpResponseRedirect


class FormList(generics.ListCreateAPIView):
    """
    APIView where the forms of the app are listed and a new form can be added.
    """
    model = Form
    queryset = Form.objects.all()
    serializer_class =  FormSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    def pre_save(self, obj):
        obj.owner = self.request.user
      

class FormDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView to see details, modify or delete a form.
    """
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    def pre_save(self, obj):
        obj.owner = self.request.user

        
class VersionList(generics.ListCreateAPIView):
    """
    APIView where the version of the selected form are listed and a new version can be added.
    """
    model = Version
    serializer_class =  VersionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    def get(self, request, pk, format=None):
        try:
            versions = Form.objects.get(id=pk).versions.all()
            serializer = VersionSerializer(versions, many=True)
            return Response(serializer.data)
        except Form.DoesNotExist:
            content = {"error": "There is no form with that slug"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    

    def post(self, request, pk, format=None):
        serializer = VersionSerializer(data=request.DATA)
        form = Form.objects.get(id=pk)
        serializer.form = form
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


class VersionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView to see details, modify or delete a form.
    """
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    def get_object(self, pk, number):
        try:
            form = Form.objects.get(id=pk)
            return form.versions.get(number=number)
        except ObjectDoesNotExist:
            content = {"error": "There is no form with that slug or the corresponding"
                       " form has no version with that number"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    

    def get(self, request, pk, number, format=None):
        version = self.get_object(pk, number)
        serializer = VersionSerializer(version)
        return Response(serializer.data)

    def put(self, request, pk, number, format=None):
        version = self.get_object(pk, number)
        serializer = VersionSerializer(version, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request,  pk, number, format=None):
        #get related form of the version that is going to be deleted
        form = Form.objects.get(id=pk)
        #get version 
        version = Version.objects.get(form=form, number=number)
        #only draft versions can be deleted this way
        if version.status == DRAFT:
            version.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    
class NewVersion(generics.CreateAPIView):
    """
    APIView to create a new version of a form or duplicate a form
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    def get(self, request, pk, number, action):
        try:
            #get version of form that is going to be duplicated-
            form = Form.objects.get(id=pk)
            version = Version.objects.get(form=form, number=number)
        except Version.DoesNotExist or Form.DoesNotExist:
            content = {"error": "There is no form with that slug or the corresponding"
                       " form has no version with that number"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        #if action new version
        if action == "new":
            #create version and save it on database
            new_version = Version(json=version.json, form=form)
            new_version.save()    
        #if action duplicate a version       
        elif action == "duplicate":
            #create a copy of the form related to selected version
            new_form = Form(title=form.title, owner=request.user)
            new_form.title += "(duplicated)"
            new_form.save()
            #create a copy of the version and save it on database
            new_version = Version(json=version.json, form=new_form)
            new_version.save()
        return HttpResponseRedirect("/dynamicForms/main/")
    
class DeleteVersion(generics.DestroyAPIView):
    """
     APIView to delete a form
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    def get(self, request,  pk, number, format=None):
        ##get related form of the version that is going to be deleted
        form = Form.objects.get(id=pk)
        #get version 
        version = Version.objects.get(form=form, number=number)
        #only draft versions can be deleted this way
        if version.status == DRAFT:
            version.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
class DeleteForm(generics.DestroyAPIView):
    """
     APIView to delete a form
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    def get(self, request, pk):
        #get form and delete it
        form = Form.objects.get(id=pk)
        form.delete()
        return HttpResponseRedirect("/dynamicForms/main/")
            
            
class FillForm(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView to retrieve current version of a form to be filled
    """
    serializer_class = VersionSerializer

    def get(self, request, slug, format=None):
        form = Form.objects.get(slug=slug)
        form_versions = Version.objects.filter(form=form)
        # Max will keep track of the highest published version
        # of the form to be displayed
        max = form_versions.filter(status=PUBLISHED).aggregate(Max('number'))
        final_version = form_versions.get(number=max['number__max'])
#         for version in form_versions:
#             if version.number > max: #and version.status == PUBLISHED:
#                 max = version.number
#                 final_version = version
        serializer = VersionSerializer(final_version)
        return Response(serializer.data)

class GetTitle(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView to get form title, since it is not included in version
    """
    serializer_class = FormSerializer

    def get(self, request, slug, format=None):
        form = Form.objects.get(slug=slug)
        serializer = FormSerializer(form)
        return Response(serializer.data)


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@api_view(['POST'])
def submit_form_entry(request, slug, format=None):
    """
    APIView to submit a Form Entry.
    """
    # TODO: agregar primera iteracion por las respuestas
    # para hacer la validacion, antes de crear el entry
    '''
    for field in request.DATA:
            serializer = FieldEntrySerializer(data=field)
            #Validar campo
            #if not validar:
                #Enviar respuesta al front con el error
    '''
    form = Form.objects.get(slug=slug)
    form_versions = Version.objects.filter(form=form)
    # Max will keep track of the highest published version
    # of the form to be displayed
    max = form_versions.filter(status=PUBLISHED).aggregate(Max('number'))
    final_version = form_versions.get(number=max['number__max'])
    # FIXME: Si se agrega el status EXPIRED, deberia haber solo 1 version PUBLISHED
    # asi que no seria necesario buscar el nro de version mas alto
    #for version in form_versions:
    #    if version.number > max: #and version.status == PUBLISHED:
    #        max = version.number
    #        final_version = version
    entry = FormEntry(version=final_version)
    entry.entry_time = datetime.now()
    entry.save() 
    for field in request.DATA:
            serializer = FieldEntrySerializer(data=field)
            if serializer.is_valid():
                serializer.save()
                #FIXME: Improve foreing key setting
                num = serializer.object.pk
                field_entry = FieldEntry.objects.get(id=num)
                field_entry.entry = entry
                field_entry.save()
    return Response(status = status.HTTP_200_OK)

@login_required
def formList(request):
    """
        Gets the list of all forms and versions from the database, and renders the template to show them
    """
    forms = Form.objects.values()
    for f in forms:
        #Obtain the list of versions of the form f ordered by version number (descendant)
        #FIX ME: improve get versions
        query_set = Form.objects.get(slug=f['slug']).versions.order_by('number').reverse()
        vers_dict = query_set.values()
        #Assign the dict of versions to the form dict
        f["versions"] = vers_dict
        #Get the status of the last version, to know if there is already a draft in this form
        if len(vers_dict) > 0:
            last_version = vers_dict[0]
            f["lastStatus"] = last_version['status']
    return render_to_response('mainPage.html', {"formList": forms})

@login_required
def editor(request):
    return render_to_response('editor.html', {})
    

@api_view(['GET'])
def get_responses(request, slug, number, format=None):
    """
    APIView to get all the entries for a particular form.
    """
    try:
        form = Form.objects.get(slug=slug)
        v = form.versions.get(number=number)
        if (v.status == DRAFT):
            content = {"error": "This version's status is Draft."}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
        queryset = v.entries.all()
        serializer = FormEntrySerializer(queryset, many=True)
        return Response(serializer.data)
    except ObjectDoesNotExist:
        content = {"error": "There is no form with that slug or the corresponding"
                   " form has no version with that number"}
        return Response(content, status=status.HTTP_404_NOT_FOUND)
    


class SimpleStaticView(TemplateView):
    def get_template_names(self):
        return [self.kwargs.get('template_name') + ".html"]
    
    def get(self, request, *args, **kwargs):
        from django.contrib.auth import authenticate, login
        if request.user.is_anonymous():
            # Auto-login the User for Demonstration Purposes
            user = authenticate()
            login(request, user)
        return super(SimpleStaticView, self).get(request, *args, **kwargs)
        
        
        
        
        
        
    
