=== To make it works ===
-Put archive_election.py in /data/django/podv3/pod. 
-Set Your bd settings => Con = MySQLdb.Connect(host="127.0.0.1", port=3306, user="pod", passwd="password", db="pod") (lg26)
- /!\ Check in the code that the row indice have the great column indice.
    For example : (lg145) print("Durée de la video : "+str(time.strftime("%H:%M:%S", time.gmtime(row[20])))) .... Is 20 the great indice of the table for the row "durée de la video" ?
    There is a chance that is not the case.

-Put yourselft in your workon and use the user pod
-Launch the script => python3 archive_election.py

=== the current equation is : CommentOnGarde = (vuesCalcul + vuesAnnesCalcul + nbJourAjoutCalcul + nbChainesCalcul + nbFavCalcul + nbCommentCalcul + rapportDureCalcul + typeCalcul + themeCalcul) / 9 ===

The coefficient are custumable at the line 225 =>>
###############################################################################
############################### Montage EQUATION ##############################
###############################################################################
