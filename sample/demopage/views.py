from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import cv2
import numpy as np
import joblib
import os

model = joblib.load(os.path.join(os.path.dirname(__file__), 'svm_rbf_model_svc.joblib'))

def home(request):
    return render(request, 'home.html')


def login(request):
    if request.method == "POST":
        un = request.POST['username']
        pw = request.POST['password']
        user = authenticate(request, username=un, password=pw)
        if user is not None:
            auth_login(request, user)
            return redirect('/profile')  # Redirect to profile after successful login
        else:
            msg = 'Invalid Username/Password'
            form = AuthenticationForm()
            return render(request, 'login.html', {'form': form, 'msg': msg})
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')  # Redirect to the login page after successful signup
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})

@login_required()
def profile(request):
    img_url = None
    result1 = None
    result2 = None
    
    if(request.method=="POST"):
        if(request.FILES.get('uploadImage')):
            img_name = request.FILES['uploadImage']
            # create a variable for our FileSystem package
            fs = FileSystemStorage()
            filename = fs.save(img_name.name,img_name)
            #urls
            img_url = fs.url(filename)
            #find the path of the image
            img_path = fs.path(filename)
 
            #start implementing the opencv condition
            img = cv2.imread(img_path,cv2.IMREAD_COLOR)
            # Convert to grayscale (single channel)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            #resize the image for a constant use
            img = cv2.resize(img,(64,64))
            #flatten the image for the better clear shape of the disease spread on the skin
            img = img.flatten()
            #using the normalization predefined function to find the value
            img = np.expand_dims(img,axis=0)
 
            #we sill start executing with our model
            predict = model.predict(img)[0]
            
            ''''''
            skin_disease_names = ['Cellulitis','Impetigo','Athlete Foot','Nail Fungus',
                                  'Ringworm','Cutaneous Larva Migrans','Chickenpox','Shingles']
            
            diagnosis = ['''Common and potentially serious bacterial skin and subcutaneous (i.e., under the  skin) tissue infections. 
                        With cellulitis, bacteria enter the skin.
                        Cellulitis may spread rapidly. Affected skin appears swollen and red and may be hot and tender.
                        Without treatment with an antibiotic, cellulitis can be life-threatening.''',

                        '''A highly contagious skin infection that causes red sores on the face.
                        Impetigo mainly affects infants and children. They are caused by group gram-positive staphylococcus aureus and group A beta-hemolytic streptococcus.
                        The main symptom is red sores that form around the nose and mouth. The sores rupture, ooze for a few days, then form a yellow-brown crust.
                        Antibiotics shorten the infection and can help prevent spread to others.''',

                        '''A fungal infection that usually begins between the toes.
                        Athlete's foot commonly occurs in people whose feet have become very sweaty while confined within tight-fitting shoes.
                        Symptoms include a scaly rash that usually causes itching, stinging and burning. People with athlete's foot can have moist, raw skin between their toes.
                        Treatment involves topical antifungal medication.''',

                        '''A nail fungus causing thickened, brittle, crumbly or ragged nails.
                        Usually, the problems caused by this condition are cosmetic.
                        The main symptoms are changes in the appearance of nails. Rarely, the condition causes pain or a slightly foul odor.
                        Treatments include oral antifungal drugs, medicated nail polish or cream or nail removal.''',

                        '''A highly contagious fungal infection of the skin or scalp.
                        Ringworm is spread by skin-to-skin contact or by touching an infected animal or object.
                        Ringworm is typically scaly and may be red and itchy. Ringworm of the scalp is common in children, where it may cause bald patches.
                        The treatment for ringworm is antifungal medication.''',

                        '''Cutaneous larva migrans (abbreviated CLM), colloquially called creeping eruption, is a skin disease in humans, caused by the larvae of various nematode parasites of the hookworm family (Ancylostomatidae).
                        The parasites live in the intestines of dogs, cats, and wild animals.
                        The infection causes a red, intensely itchy eruption and may look like twirling lesions.
                        The itching can become very painful and if scratched may allow a secondary bacterial infection to develop.
                        Cutaneous larva migrans usually heals spontaneously over weeks to months and has been known to last as long as one year.
                        However the severity of the symptoms usually causes those infected to seek medical treatment before spontaneous resolution occurs.
                        After proper treatment, migration of the larvae within the skin is halted and relief of the associated itching can occur in less than 48 hours.
                        Albendazole is a very effective treatment for CLM.''',

                        '''A highly contagious viral infection which causes an itchy, blister-like rash on the skin.
                        Chickenpox is highly contagious to those who haven't had the disease or been vaccinated against it.
                        The most characteristic symptom is an itchy, blister-like rash on the skin.
                        Chickenpox can be prevented by a vaccine. Treatment usually involves relieving symptoms, although high-risk groups may receive antiviral medication.
                        ''',
                        
                        '''Shingles are a viral infection that usually occurs in adults and causes a painful rash.
                        Anyone who has had chickenpox may develop shingles. It is not known what causes the virus to reactivate. Shingles may occur anywhere in your body.
                        Shingles cause a painful rash that may appear as a stripe of blisters on the dermatomal distribution. Pain can persist even after the rash is gone (this is called post-herpetic neuralgia).
                        Treatments include pain relief (nonsteroidal anti-inflammatory drugs [NSAIDs] and antiviral medications such as Acyclovir, Valacyclovir, Famciclovir, and numbing medications such as Lidocaine).
                        A chickenpox vaccine in childhood or a shingles vaccine in adulthood can minimize the risk of developing complications.'''
                        ]
 
            result1 = skin_disease_names[predict]
            result2 = diagnosis[predict]
 
    return render(request,'profile.html',{'img':img_url,'obj1':result1,'obj2':result2})
