from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
from . import util
import random
import markdown2



class EntryForm(forms.Form):
    title = forms.CharField()


def index(request):
    util.del_entry("Test page")
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry_view(request, entry_name):
    
    if entry_name not in util.list_entries():
        #redirect to error page
        return render(request, "encyclopedia/e404.html", context = {"entry": entry_name})
    
    else:
        # Get string from entry file
        entry_page = util.get_entry(entry_name)
        # Convert to html
        
        md = markdown2.markdown(entry_page).replace("\n","")
        
        # Render html
        return render(request, "encyclopedia/entry.html", context= {"t": entry_name, "md": md})

def query_search(request):
    query = request.GET.get("q", "")
    query = query.strip()
    #query = request.GET['q']
    if query!="":
        
        matches = set()
        # Query found: Return wiki page
        for entry in util.list_entries():
            if entry.lower() == query.lower():
                #return entry_view(request, entry)
                return HttpResponseRedirect((reverse("entry_site", args={entry:None})))
            
            # Query not found: Find a possible match
            else:
                if query.lower() in entry.lower():
                    matches.add(entry)
        
        if len(matches) == 0: matches = None
        return render(request, "encyclopedia/search.html", 
            context = {"matches":matches, "query":query})

    #No search query - Reload home page
    return index(request)

def create_new_page(request):
    if request.method == "POST":
        new_form = EntryForm(request.POST)
        if new_form.is_valid():
            title = new_form.cleaned_data.get('title')

            #Redirect to new page of newly created wiki
            md = request.POST.get("markdown", "")
            for entry in util.list_entries():
                if entry.lower() == title.lower():
                    error = f"{entry} already exists"
                    return render(request, "encyclopedia/create-new.html", 
                        context={"new_page_form":new_form, "text_area_value": md, 
                        "error_message":error})


            if md == "":
                error = "No Markdown content inserted"
                return render(request, "encyclopedia/create-new.html", 
                        context={"new_page_form":new_form, "text_area_value": md, 
                        "error_message":error})

            util.save_entry(title, md)
            #return entry_view(request, title)
            return HttpResponseRedirect((reverse("entry_site", args=[title])))

    return render(request, "encyclopedia/create-new.html", 
                context={"new_page_form":EntryForm})

def edit_page(request):
    if request.method == "GET":

        title = request.GET.get('title','')
        if title !='':
            md = util.get_entry(title).strip()
 
            return render(request, "encyclopedia/edit.html",
                context={"t":title, "edit_data": md})

    elif request.method == "POST":

        #Save content
        title = request.POST.get('title',"").strip()
        md = request.POST.get("markdown", "")
     
        md = md.replace("\n", "").strip()
        util.save_entry(title, md)

        return HttpResponseRedirect((reverse("entry_site", args=[title])))

def random_page(request):
    entries = util.list_entries()
    rand = random.randint(0, len(entries)-1)
    
    title = entries[rand]
    #return entry_view(request, title)
    return HttpResponseRedirect((reverse("entry_site", args=[title])))

def delete_page(request):
    if request.method == "GET":
        #Display website to choose entry to delete
        return render(request, "encyclopedia/delete.html", 
                      context={"entries":util.list_entries(), "display_buttons":False})
        
    if request.method == "POST":
        #Adds 2 buttons to ask user to confirm delete
        title = request.POST.get("title", "")
        display_buttons = request.POST.get("display_buttons", "")
        delete = request.POST.get("del", "")
        print(f'display_button=={display_buttons} delete=={delete} title={title}')
        if title != "":
            for entry in util.list_entries():
                if entry.lower() == title.lower():
                    
                    if display_buttons == "F": #User entered a title to be deleted
                        return render(request, "encyclopedia/delete.html", 
                              context={"entries":util.list_entries(), "display_buttons":True, "title":entry})
                        
                    elif display_buttons == "T":
                        
                        if delete == "Yes":
                            util.del_entry(entry)        
                        return HttpResponseRedirect(reverse("index"))
            
            # Title Not found - Display error and list of entries
            error = f"{title} doesn't exist in entries"
            return render(request, "encyclopedia/delete.html", 
                    context={"entries":util.list_entries(), "error_message":error})
        # No title - display list of entries     
        else:
            return render(request, "encyclopedia/delete.html", 
                      context={"entries":util.list_entries()})