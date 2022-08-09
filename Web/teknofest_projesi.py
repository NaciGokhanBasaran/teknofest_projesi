from flask import Flask,redirect,url_for,render_template,request,session
import requests    
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from flask import send_file
import twint



app =Flask(__name__)
app.secret_key = "hello"


def hepsi_burada(link,agent,limit=20,degerleri_yazdir=True,kaydet=True):
    url = f"https://www.hepsiburada.com/{link}-yorumlari"
    r = requests.get(url,headers=agent)
    soup = BeautifulSoup(r.content,"html.parser")
   
    sayfa_sayisi=soup.find_all("span",{"class":"hermes-PageHolder-module-mgMeakg82BKyETORtkiQ"})
    sayfa_sayisi= str(sayfa_sayisi[-1].text)
    print(sayfa_sayisi)
    yazilar=[]

    for i in range(1,int(sayfa_sayisi)//2):#hepsi buradada toplam yorum sayısının yarısından fazlasını almaya çalıştığınızda ilk yorumlar sayfasına gönderiliyorsunuz.
        if i>limit:
            break

        else:
            yeni_url=url+"?sayfa="+str(i)
            r = requests.get(yeni_url,headers=agent)
            soup = BeautifulSoup(r.content,"html.parser")
            yorumlar =soup.find_all("div",{"class":"hermes-ReviewCard-module-KaU17BbDowCWcTZ9zzxw"})

            for a in yorumlar:
                yorum =a.text.split("Değerlendirilen özellikler")
                yorum=str(yorum[0])
                yazilar.append(yorum)
                if degerleri_yazdir ==True:
                    print(yorum+"\n")

            if degerleri_yazdir ==True:
                print("----------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    
    return pd.DataFrame(yazilar,columns =['Metin']) 
    
         
def turkce_harfleri_degistir(x):
   #stringdeki (ü,o,ş,ğ,ı,c) harflerini (u,o,s,g,i,c) ile değiştirecek
    x = x.replace('ü', 'u')
    x = x.replace("ö","o")
    x = x.replace("ş","s")
    x = x.replace("ğ","g")
    x = x.replace("ı","i")
    x = x.replace("ç","c")
    return x
def metin_temizle_eksi(x):
  yeni_metin = []

  for i in x:
    i = i.replace('\r','')
    i = i.replace('\n','')
    i = i.replace('$','s')
    i = i.replace('  ',' ')
    
    if i[:6]!=" (bkz:" and i[:7]!="  (bkz:":

      yeni_metin.append(i)

  return yeni_metin


def eksi_sozluk(isim:str,agent,limit=20,degerleri_yazdir=False):

        isim = turkce_harfleri_degistir(isim)
        url =f"https://eksisozluk.com/{isim}"
        r =requests.get(url,headers=agent)
        soup =BeautifulSoup(r.content,"html.parser")

        topicid=soup.find("div",{"class":"lazy"})
        sayfa_sayisi = soup.find("div",{"class":"pager"})

        topicid=str(topicid)
        sayfa_sayisi=str(sayfa_sayisi)

        topicid = ''.join(x for x in topicid if x.isdigit())
        sayfa_sayisi = ''.join(x for x in sayfa_sayisi if x.isdigit())
        sayfa_sayisi=(sayfa_sayisi[1:])

    
    
        isim = isim.replace(" ","-")

        yazilar=[]

        if (sayfa_sayisi or topicid)== "":
            print("Böyle bir entry bulunamadı ")
            return 0 

        else:

            for i in range(1,int(sayfa_sayisi)):
                if i>limit :
                    break

                else:
                    url =f"https://eksisozluk.com/{isim}--{topicid}?p={i}"
                    if degerleri_yazdir ==True:
                        print(f"url:\n{url}")
                    r =requests.get(url,headers=agent)

                    soup =BeautifulSoup(r.content,"html.parser")

                    yorumlar =soup.find_all("div",{"class":"content"})

                    for y in yorumlar:
                        yazilar.append(y.text)
                        if degerleri_yazdir ==True:
                            print(y.text)


            yazilar = metin_temizle_eksi(yazilar)
            return  pd.DataFrame(yazilar,columns =['Metin'])



def twitter(isim,limit:int=10,baslangic:str="2015-01-24 00:00:00",
                bitis:str ='2022-07-21 00:00:00',kaydet:bool=True,dosya_adi:str="-"):


                t =twint.Config()
                t.Search = isim
                t.Limit =limit
                t.Since = baslangic
                t.Until = bitis
                
                if kaydet==True:
                    t.Store_csv = True,
                    
                    if dosya_adi =="-":
                        yeni_dosya_adi=isim+str(random.randint(10000,100000))+".csv"
                    else:
                        yeni_dosya_adi = dosya_adi+".csv"
                    t.Output=yeni_dosya_adi
            
                twint.run.Search(t)
   
   


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/veri")
def veri():
    return render_template("veri.html")


@app.route("/veri/hepsiburada",methods =["POST","GET"])
def hepsiburada():

    return render_template("hepsiburada.html")



@app.route("/veri/hepsiburada/indir",methods =["GET", "POST"])
def hepsiburada_indir():

    if request.method == "POST":
      
       link = str(request.form.get("link"))
       agent = str(request.form.get("agent"))
       limit = int(request.form.get("limit"))
       dosya_adi = str(request.form.get("dosya_adi"))
       uzanti = str(request.form.get("uzantı"))
       
       agent={"User-Agent":agent}
       yazilar_pd= hepsi_burada(link =link,agent =agent,limit = limit)
       
       
       dosya_adi =dosya_adi+"."+uzanti

       if uzanti =="csv":
            yazilar_pd.to_csv(dosya_adi,index=False)   
       else:
            yazilar_pd.to_excel(dosya_adi,index=False)   
       return send_file(dosya_adi, as_attachment=True)                       
        #return render_template("hepsiburadaveri.html",a=yazilar)
    else:
        return render_template("hepsiburada.html")



@app.route("/veri/eksisozluk")
def eksisozluk():
    return render_template("eksisozluk.html")



@app.route("/veri/eksisozluk/indir",methods=["GET", "POST"])
def eksisozluk_indir():  
    if request.method == "POST":
      
       isim = str(request.form.get("link"))
       agent = str(request.form.get("agent"))
       limit = int(request.form.get("limit"))
       dosya_adi = str(request.form.get("dosya_adi"))
       uzanti = str(request.form.get("uzantı"))
       
       agent={"User-Agent":agent}
       yazilar_pd = eksi_sozluk(isim = isim,agent = agent,limit = limit)
       dosya_adi =dosya_adi +"."+uzanti
       if uzanti =="csv":
            yazilar_pd.to_csv(dosya_adi,index=False)   
       else:
            yazilar_pd.to_excel(dosya_adi,index=False)   
       
       return send_file(dosya_adi, as_attachment=True)                       
        
    else:  
        return render_template("hepsiburada.html")



@app.route("/veri/twitter")
def twitter():
    return render_template("twitter.html")



@app.route("/veri/eksisozluk/twitter",methods=["GET", "POST"])
def twitter_indir():  
    if request.method == "POST":
      
       isim = str(request.form.get("link"))
       kaydet =True
       uzanti = str(request.form.get("uzantı"))
       limit = int(request.form.get("limit"))
       dosya_adi = str(request.form.get("dosya_adi"))
       t =twint.Config()
       t.Search = isim
       t.Limit =limit
       
                
       if uzanti=="csv":

            t.Store_csv = True
            if dosya_adi =="-":
                yeni_dosya_adi=isim+str(random.randint(10000,100000))+".csv"
            else:
                yeni_dosya_adi = dosya_adi+".csv"
       else:
            t.Store_excel = True
            if dosya_adi =="-":
                yeni_dosya_adi=isim+str(random.randint(10000,100000))+".xlsx"
            else:
                yeni_dosya_adi = dosya_adi+".xlsx"

       t.Output=yeni_dosya_adi
            
       twint.run.Search(t)
      
       
       
       return send_file(yeni_dosya_adi, as_attachment=True)                       
        
    else:  
        return render_template("hepsiburada.html")



if __name__ == "__main__":
    app.run(debug =True)
