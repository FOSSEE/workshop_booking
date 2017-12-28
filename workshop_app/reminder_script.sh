path=$1 #command line argument to virtual environment

DIR="$( cd "$( dirname "$0" )" && pwd )"
cd $DIR

#Activate virtual environment
source $1bin/activate 
#Run script to send reminder mails
python reminder_script.py
#Train chatbot
cd ..
python manage.py train
#Deactivate Virtual environment
deactivate
