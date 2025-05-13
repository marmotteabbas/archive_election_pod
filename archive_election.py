from django.conf import settings
from django.utils import translation
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _
from django.template.defaultfilters import striptags
from django.core.mail import send_mail

# from django.core.mail import mail_admins
from django.core.mail import mail_managers
from django.contrib.sites.shortcuts import get_current_site
import csv
import os

import MySQLdb
import time

from datetime import datetime


print("Lets take some information in the bdd")
#https://docs.djangoproject.com/en/5.1/topics/db/sql/
#https://python.doctor/page-database-data-base-donnees-query-sql-mysql-postgre-sqlite
#https://www.datacamp.com/fr/tutorial/tutorial-how-to-execute-sql-queries-in-r-and-python
#https://stackoverflow.com/questions/11121819/mysqldb-in-python-cant-connect-to-mysql-server-on-localhost

Con = MySQLdb.Connect(host="127.0.0.1", port=3306, user="pod", passwd="xxxxxxx", db="pod")
Cursor = Con.cursor()



#request to get view counting of a specific video
sql_count = "SELECT * FROM video_viewcount order by video_id"
Cursor.execute(sql_count)
rowcount = Cursor.fetchone()
array_count = {}

#such a shitty langage ... set all the tab init
for rowcount in Cursor :
  array_count[rowcount[3]] = []

for rowcount in Cursor :
    array_count[rowcount[3]].append([str(rowcount[0]), str(rowcount[1]), str(rowcount[2]), str(rowcount[3])])

#########################################
########## fetch all info ###############
#########################################
sql = "SELECT * FROM video_video"
Cursor.execute(sql)
row = Cursor.fetchone()

all_data_csv = []

#render all the infos
for row in Cursor:
  # That's where we gonna store the date for the CSV file diffusion
  data_to_add = {}

  # ------------ Affichage du titre ------------ #
  print("--- (" + str(row[0])+") "+str(row[3])+"---")

  #Add data for csv
  data_to_add['id_video'] = row[0]
  data_to_add['name_video'] = row[3]

# ------------ Comptage du nombres de vues sur une video ------------ #
  try:
    comptage_de_vues = 0
    for row_count in array_count[row[0]] :
        comptage_de_vues += int(row_count[2])
    print (str(comptage_de_vues) + " vues")
  except KeyError:
    comptage_de_vues =0
    print('0 vues')

  data_to_add['nb_de_vues'] =comptage_de_vues

  # ------------ Comptage par date y'a 1 ans ------------ #
  comptage_dernières_annees = 0
  today = datetime.now()
  try:
    for row_count in array_count[row[0]]:
      someday = datetime.strptime(row_count[1], '%Y-%m-%d')
      diff =  today - someday
      if (int(diff.days) < 365):
        comptage_dernières_annees = comptage_dernières_annees + int(row_count[2])

    print(str(comptage_dernières_annees) + " vues cette dernière années")

  except KeyError:
        print('0 vues ces 12 derniers mois')
        comptage_dernières_annees=0

  data_to_add['nb_de_vues_dernière_annee'] = comptage_dernières_annees

  # ------------ Date d'ajout ------------ #
  today = datetime.now()
  #someday = datetime.strptime(str(row[9]), '%Y-%m-%d %h:%m:%s')
  diff = today - row[9]

  print("Ajout sur la platform : " + str(row[9])+" // Soit il y a : " +str(diff.days)+" Jours")

  data_to_add['date_ajout'] = row[9]
  data_to_add['nb_jours_depuis_ajout'] = diff.days

  # ------------ Nombre de channel ------------ #
  sql_count = "SELECT * FROM video_video_channel Where video_id ="+str(row[0])
  Cursor.execute(sql_count)

  couting_channel=0

  rowchannelcount = Cursor.fetchone()
  for rowchannelcount in Cursor:
    if(rowchannelcount[2]>=1):
      couting_channel=couting_channel+1

  print("Cette video appartient à "+str(couting_channel)+" chaines")
  data_to_add['nb_de_chaine'] = couting_channel

  # ------------ nombre de favoris ------------ #
  sql_playlist = "SELECT ppone.id FROM video_video vv INNER JOIN playlist_playlistcontent pp ON vv.id = pp.video_id INNER JOIN playlist_playlist ppone ON ppone.id = pp.playlist_id WHERE ppone.name='Favorites' AND vv.id="+str(row[0])
  Cursor.execute(sql_playlist)

  comptagefav = 0
  rowfavoritecount = Cursor.fetchone()

  for rowfavoritecount in Cursor:
    comptagefav = comptagefav+1

  print("Nombre de fois favoris : "+str(comptagefav))
  data_to_add['nb_de_fav'] = comptagefav

  # ------------ nombre de commentaires ------------ #
  sql_comment = "SELECT * FROM video_comment WHERE video_id ="+str(row[0])
  Cursor.execute(sql_comment)
  rowcomment = Cursor.fetchone()

  commentcount = 0
  for rowcomment in Cursor:
    commentcount = commentcount+1

  print('Nombre de commentaires :'+str(commentcount))
  data_to_add['nb_de_comment'] = commentcount

  # ------------ Durée de la vidéo ------------ #
  print("Durée de la video : "+str(time.strftime("%H:%M:%S", time.gmtime(row[21]))))
  data_to_add['duree_video'] = time.strftime("%H:%M:%S", time.gmtime(row[21]))

  # ------------ video type ------------ #
  sql_type = "SELECT vv.title, vt.title AS title_type FROM video_video vv INNER JOIN video_type vt ON vv.type_id = vt.id WHERE vv.id = "+str(row[0])+" LIMIT 1"
  Cursor.execute(sql_type)
  rowtype = Cursor.fetchone()
  print("type de la video : "+rowtype[1])
  data_to_add['type_video'] = rowtype[1]

  # ------------ video theme ------------ #

  sqltheme = "SELECT vv.id, vv.title, vt.id AS theme_id, vt.title AS theme_name FROM video_video_channel vvc INNER JOIN video_video vv ON vv.id = vvc.video_id INNER JOIN video_theme vt " + "ON vt.channel_id = vvc.id WHERE vv.id = "+str(row[0])

  Cursor.execute(sqltheme)
  rowtheme = Cursor.fetchone()

  theme_list = []

  themes_video = ""
  for rowtheme in Cursor:
    themes_video = themes_video + str(rowtheme[3])+"("+str(rowtheme[2])+")"
    themes_video = themes_video + ", "

    theme_list.append(rowtheme[3])

  themes_video = themes_video[:-2]

  if (themes_video==""):
    print("Theme(s) de la video : Aucun")
    data_to_add['theme_video'] = "Aucun"

  else:
    print("Theme(s) de la video : "+themes_video)
    data_to_add['theme_video'] = themes_video

  # ------------ video Owner ------------ #
  sql_owner = "SELECT au.username, au.email FROM video_video v INNER JOIN auth_user au ON v.owner_id = au.id  Where v.id =" + str(row[0])
  Cursor.execute(sql_owner)
  rowowner = Cursor.fetchone()

  print("Le propriétaire de la vidéo est :"+rowowner[0]+" ("+rowowner[1]+")")

  data_to_add['owner_video'] = rowowner[1]

  # ------------ Owner Aditionnal ------------ #
  sql_owneradi = ("SELECT au.username, au.email FROM video_video_additional_owners vvao LEFT JOIN auth_user au ON au.id = vvao.user_id  WHERE vvao.video_id = " + str(row[0]))

  Cursor.execute(sql_owneradi)
  rowowneradi = Cursor.fetchone()

  if rowowneradi is not None:
    print("\rIl y a propriétaire(s) additionnel(s) : ", end='', flush=True)
  else:
    print("Il n'y a PAS de propriétaire additionnel")

  list_additionnal_owner = ""
  for rowowneradi in Cursor:
      list_additionnal_owner = list_additionnal_owner+(rowowneradi[0]+" ("+rowowneradi[1]+") ")
      print(rowowneradi[0]+" ("+rowowneradi[1]+") ")

  data_to_add['additional_owner'] = list_additionnal_owner

  # ------------ Categorie ------------ #
  sql_categ = "SELECT vc.title FROM video_category_video vcv INNER JOIN video_category vc ON vc.id = vcv.category_id WHERE video_id="+str(row[0])
  Cursor.execute(sql_categ)
  rowcateg = Cursor.fetchone()

  if rowcateg is not None:
    print("\rCette video apparteient à categorie(s) : ", end='', flush=True)
  else:
    print("Cette vidéo n'appartient pas à une categorie.")

  categ = ""
  for rowcateg in Cursor:
    categ = categ+rowcateg[0]+" "
    print(rowcateg[0]+" ")

  data_to_add['categ'] = categ

  ###############################################################################
  ############################### Montage EQUATION ##############################
  ###############################################################################
  coefVues = 0.02
  coefVuesAnnes = 0.04
  coefJoursAjout = 1
  coefNbChaines = 6
  coefNbFavoris = 3
  coefNbComments = 1
  coefDureeVideo = 1

  ## Value Type Coef ##
  coefTypeVideo = 2

  typeValue = {}
  typeValue['Supports pédagogiques'] = 50
  typeValue['Conférences'] = 40
  typeValue['Colloque'] = 40
  typeValue['Production étudiante'] = 30
  typeValue['Tutoriels'] = 40
  typeValue['Films promotionnels'] = 10
  typeValue['Documentaires'] = 10
  typeValue['Audio'] = 10
  typeValue['Autres'] = 10
  typeValue['Relation presse'] = 10
  typeValue['Films institutionnels'] = 10

  ## Value Theme Coef ##
  themeValue = {}
  themeValue['Aucun'] = 0

  coefThemeCalcul = 2



  ## Get respons from owner ##

  ############TOTAL EQUATION ############
  ## Vues Valeur Calcul (vuesCalcul)##
  vuesCalcul = data_to_add['nb_de_vues'] * coefVues
  #print (vuesCalcul)

  ## Vues Valeur Calcul (vuesAnnesCalcul) ##
  vuesAnnesCalcul = data_to_add['nb_de_vues_dernière_annee'] * coefVuesAnnes
  #print(vuesAnnesCalcul)

  ## Jour Ajout Calcul (nbJourAjoutCalcul) ##
  if data_to_add['nb_jours_depuis_ajout'] < 1:
    data_to_add['nb_jours_depuis_ajout'] = 1

  nbJourAjoutCalcul = (360 / data_to_add['nb_jours_depuis_ajout']) * coefJoursAjout
  #print (nbJourAjoutCalcul)

  ## Nb de Chaine Calcul (nbChainesCalcul) ##
  nbChainesCalcul = data_to_add['nb_de_chaine'] * coefNbChaines
  #print(nbChainesCalcul)

  ## Nb Favoris Calcul (nbFavCalcul) ##
  nbFavCalcul = data_to_add['nb_de_fav'] * coefNbFavoris
  #print (nbFavCalcul)

  ## Nb Commentaires Calcul (nbCommentCalcul) ##
  nbCommentCalcul = data_to_add['nb_de_comment'] * coefNbComments
  #print (nbCommentCalcul)

  ## Dure video calcul (rapportDureCalcul) ##
  nbHeurs = datetime.strptime(data_to_add['duree_video'], '%H:%M:%S').time().strftime('%H')
  nbMinuts = datetime.strptime(data_to_add['duree_video'], '%H:%M:%S').time().strftime('%M')
  nbSecs = datetime.strptime(data_to_add['duree_video'], '%H:%M:%S').time().strftime('%S')

  minutsInSec = int(nbMinuts)*60
  hourInSeconds = int(nbHeurs)*3600

  dureeFinalSec = (minutsInSec + hourInSeconds + int(nbSecs))

  if dureeFinalSec != 0:
    rapportDureCalcul = ((data_to_add['nb_de_vues_dernière_annee'] / dureeFinalSec)*100) * coefDureeVideo
  else:
    rapportDureCalcul = 0
  #print(rapportDureCalcul)

  ## Type Calcul ##
  try:
    typeCalcul = typeValue[data_to_add['type_video']] * coefTypeVideo
  except KeyError:
    typeCalcul = 0

  ## THEME Calcul ##
  themeCalcul = 0
  for t in theme_list:
    try:
        themeCalcul = themeCalcul + themeValue[str(t)]
    except KeyError:
        themeCalcul = themeCalcul + 2
  themeCalcul = themeCalcul * coefThemeCalcul



  ########################### Grande Equation ###########################
  #print equation
  print("")
  print("R = ("+str(vuesCalcul)+" (Vues) + "+str(vuesAnnesCalcul)+" (Vues Annees) + "+str(nbJourAjoutCalcul)+" (360 / Nb Jours Ajout) + "
        +str(nbChainesCalcul)+" (Nb Chaines) + "+str(nbFavCalcul)+" (Nb Favoris) + "+str(nbCommentCalcul)+" (Nb Comments) + "
        +str(rapportDureCalcul)+" (VuesAnnes/Durée)) + "+str(typeCalcul)+ " (Type) + " + str(themeCalcul) + " (Theme)"+" / 9" )

  CommentOnGarde = (vuesCalcul + vuesAnnesCalcul + nbJourAjoutCalcul + nbChainesCalcul + nbFavCalcul + nbCommentCalcul + rapportDureCalcul + typeCalcul + themeCalcul) / 9
  print ("R = "+str(CommentOnGarde))

  data_to_add['equation_result'] = CommentOnGarde
  ###############################################################################
  ###############################################################################
  ###############################################################################

  all_data_csv.append(data_to_add)
  print("\n")

#########################################
##### Ecrire data dans le csv ###########
#########################################
#https://docs.python.org/3/library/csv.html
with open('data_video.csv', 'w', newline='') as csvfile:
    fieldnames = ['id_video', 'name_video', 'nb_de_vues', 'nb_de_vues_dernière_annee','date_ajout','nb_jours_depuis_ajout','nb_de_chaine','nb_de_fav','nb_de_comment','duree_video','type_video','theme_video','owner_video','additional_owner','categ','equation_result']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    #writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
    #writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})

    #data_to_add_in_csv = {}
    #data_to_add ['first_name'] = 'huberttttttttt'
    #data_to_add ['last_name'] = 'dubedouuuuuuuuu'
    #writer.writerow(data_to_add)

    for  n in all_data_csv:
      writer.writerow(n)

